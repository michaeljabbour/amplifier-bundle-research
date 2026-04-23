"""
checklist.py — Integrity contract definitions and pure check functions.

Each check returns a CheckResult with:
  - name:     check function name (str)
  - status:   CheckStatus.PASS | FAIL | WARN | SKIP
  - message:  human-readable summary
  - evidence: dict of numeric details for report rendering
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Enums & data-classes
# ---------------------------------------------------------------------------

# Matches any bracketed single-token placeholder such as [HANDLER_ERROR],
# [ITEM_TIMEOUT], [PIPELINE_FAILURE], etc.
_ERROR_RESPONSE_RE = re.compile(r"^\[[\w_]+\]$")


def is_error_response(response: str) -> bool:
    """Return True if *response* is a pipeline-failure placeholder."""
    return bool(_ERROR_RESPONSE_RE.match(response.strip()))


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrityContract:
    """Configurable thresholds for the integrity audit.

    All fields have research-appropriate defaults; override any via keyword
    arguments when constructing the contract.
    """

    handler_error_threshold: float = 0.05
    min_response_median_chars: int = 100
    max_short_response_fraction: float = 0.05
    short_response_chars: int = 10
    max_duplicate_fraction: float = 0.1
    warn_if_accuracy_below: float = 0.01
    baseline_expected_range: tuple[float, float] = (0.01, 0.25)
    help_hurt_ratio_min: float = 0.2
    help_hurt_ratio_max: float = 5.0
    manifest_required_fields: list[str] = field(
        default_factory=lambda: ["judge_model", "split_sha256", "execution_seed"]
    )


# ---------------------------------------------------------------------------
# 1. Completeness checks
# ---------------------------------------------------------------------------


def check_row_count(
    records: list[dict],
    expected_n_items: int,
    expected_n_approaches: int,
) -> CheckResult:
    """Verify total record count equals expected_n_items × expected_n_approaches."""
    expected = expected_n_items * expected_n_approaches
    actual = len(records)
    if actual == expected:
        return CheckResult(
            "check_row_count",
            CheckStatus.PASS,
            f"{actual}/{expected} records present",
            evidence={"actual": actual, "expected": expected},
        )
    return CheckResult(
        "check_row_count",
        CheckStatus.FAIL,
        f"{actual}/{expected} records present ({expected - actual} missing)",
        evidence={"actual": actual, "expected": expected, "missing": expected - actual},
    )


def check_handler_error_rate(
    records: list[dict],
    threshold: float = 0.05,
) -> CheckResult:
    """Check that the fraction of error-placeholder responses is below *threshold*."""
    if not records:
        return CheckResult(
            "check_handler_error_rate",
            CheckStatus.SKIP,
            "No records to check",
            evidence={"rate": 0.0, "count": 0, "threshold": threshold},
        )
    error_count = sum(1 for r in records if is_error_response(r.get("response", "")))
    rate = error_count / len(records)
    evidence = {"rate": rate, "count": error_count, "total": len(records), "threshold": threshold}
    if rate > threshold:
        return CheckResult(
            "check_handler_error_rate",
            CheckStatus.FAIL,
            f"{rate * 100:.1f}% error responses (threshold {threshold * 100:.1f}%)",
            evidence=evidence,
        )
    return CheckResult(
        "check_handler_error_rate",
        CheckStatus.PASS,
        f"{rate * 100:.1f}% error responses (threshold {threshold * 100:.1f}%)",
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# 2. Response sanity checks
# ---------------------------------------------------------------------------


def check_response_length_distribution(
    records: list[dict],
    min_median: int = 100,
    max_short_fraction: float = 0.05,
    short_chars: int = 10,
) -> CheckResult:
    """Check that response lengths are plausible.

    Fails when:
    - The median response length is below *min_median*, OR
    - The fraction of responses shorter than *short_chars* exceeds
      *max_short_fraction*.
    """
    if not records:
        return CheckResult(
            "check_response_length_distribution",
            CheckStatus.SKIP,
            "No records to check",
        )
    lengths = [len(r.get("response", "")) for r in records]
    median_len = statistics.median(lengths)
    short_count = sum(1 for ln in lengths if ln < short_chars)
    short_fraction = short_count / len(lengths)

    evidence = {
        "median_chars": median_len,
        "short_fraction": short_fraction,
        "short_count": short_count,
        "total": len(lengths),
    }
    failures = []
    if median_len < min_median:
        failures.append(f"median {median_len:.0f} < {min_median} chars")
    if short_fraction > max_short_fraction:
        failures.append(
            f"{short_fraction * 100:.1f}% short responses "
            f"(threshold {max_short_fraction * 100:.1f}%)"
        )
    if failures:
        return CheckResult(
            "check_response_length_distribution",
            CheckStatus.FAIL,
            "; ".join(failures),
            evidence=evidence,
        )
    return CheckResult(
        "check_response_length_distribution",
        CheckStatus.PASS,
        f"Median {median_len:.0f} chars, {short_fraction * 100:.1f}% short responses",
        evidence=evidence,
    )


def check_no_duplicate_responses(
    records: list[dict],
    max_duplicate_fraction: float = 0.1,
) -> CheckResult:
    """Check for a stuck generator by detecting excessive duplicate responses."""
    if not records:
        return CheckResult("check_no_duplicate_responses", CheckStatus.SKIP, "No records to check")
    responses = [r.get("response", "") for r in records]
    from collections import Counter

    counts = Counter(responses)
    # Records whose response appears more than once
    duplicate_count = sum(cnt for cnt in counts.values() if cnt > 1)
    duplicate_fraction = duplicate_count / len(responses)

    evidence = {
        "duplicate_fraction": duplicate_fraction,
        "duplicate_count": duplicate_count,
        "unique_count": len(counts),
        "total": len(responses),
    }
    if duplicate_fraction > max_duplicate_fraction:
        return CheckResult(
            "check_no_duplicate_responses",
            CheckStatus.FAIL,
            (
                f"{duplicate_fraction * 100:.1f}% duplicate responses "
                f"(threshold {max_duplicate_fraction * 100:.1f}%)"
            ),
            evidence=evidence,
        )
    return CheckResult(
        "check_no_duplicate_responses",
        CheckStatus.PASS,
        f"{duplicate_fraction * 100:.1f}% duplicate responses",
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# 3. Judge integrity checks
# ---------------------------------------------------------------------------


def check_judge_coverage(records: list[dict]) -> CheckResult:
    """Verify every record has *correct_by_judge* populated (not None)."""
    if not records:
        return CheckResult("check_judge_coverage", CheckStatus.SKIP, "No records to check")
    missing = [r for r in records if r.get("correct_by_judge") is None]
    evidence = {"missing_count": len(missing), "total": len(records)}
    if missing:
        return CheckResult(
            "check_judge_coverage",
            CheckStatus.FAIL,
            f"{len(missing)}/{len(records)} records missing correct_by_judge",
            evidence=evidence,
        )
    return CheckResult(
        "check_judge_coverage",
        CheckStatus.PASS,
        f"All {len(records)} records have correct_by_judge populated",
        evidence=evidence,
    )


def check_judge_distribution(
    records: list[dict],
    warn_if_accuracy_below: float = 0.01,
) -> CheckResult:
    """Warn when overall accuracy is suspiciously low (possible judge/data bug)."""
    if not records:
        return CheckResult("check_judge_distribution", CheckStatus.SKIP, "No records to check")
    judged = [r for r in records if r.get("correct_by_judge") is not None]
    if not judged:
        return CheckResult(
            "check_judge_distribution",
            CheckStatus.SKIP,
            "No judged records available",
        )
    accuracy = sum(1 for r in judged if r["correct_by_judge"]) / len(judged)
    evidence = {"accuracy": accuracy, "correct": int(accuracy * len(judged)), "total": len(judged)}
    if accuracy < warn_if_accuracy_below:
        return CheckResult(
            "check_judge_distribution",
            CheckStatus.WARN,
            (
                f"Overall accuracy {accuracy * 100:.2f}% is suspiciously low "
                f"(warn threshold {warn_if_accuracy_below * 100:.1f}%)"
            ),
            evidence=evidence,
        )
    return CheckResult(
        "check_judge_distribution",
        CheckStatus.PASS,
        f"Overall accuracy {accuracy * 100:.2f}%",
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# 4. Provenance checks
# ---------------------------------------------------------------------------


def check_manifest_present(experiment_dir: Path) -> CheckResult:
    """Verify that a manifest file exists in *experiment_dir*."""
    for name in ("manifest.json", "experiment_meta.json"):
        if (experiment_dir / name).exists():
            return CheckResult(
                "check_manifest_present",
                CheckStatus.PASS,
                f"Found {name}",
                evidence={"filename": name},
            )
    return CheckResult(
        "check_manifest_present",
        CheckStatus.WARN,
        "No manifest.json or experiment_meta.json found — provenance unverified",
        evidence={},
    )


def check_manifest_fields(
    manifest: dict,
    required: list[str] | None = None,
) -> CheckResult:
    """Verify that *manifest* contains all *required* fields."""
    if required is None:
        required = ["judge_model", "split_sha256", "execution_seed"]
    missing = [f for f in required if f not in manifest]
    evidence = {"required": required, "missing": missing}
    if missing:
        return CheckResult(
            "check_manifest_fields",
            CheckStatus.FAIL,
            f"Missing required fields: {', '.join(missing)}",
            evidence=evidence,
        )
    return CheckResult(
        "check_manifest_fields",
        CheckStatus.PASS,
        f"All required fields present: {', '.join(required)}",
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# 5. Statistical sanity checks
# ---------------------------------------------------------------------------


def check_baseline_plausibility(
    records: list[dict],
    expected_range: tuple[float, float] = (0.01, 0.25),
) -> CheckResult:
    """Warn when C0/A0 baseline accuracy falls outside *expected_range*."""
    baseline = [r for r in records if r.get("approach_id") == "A0"]
    if not baseline:
        return CheckResult(
            "check_baseline_plausibility",
            CheckStatus.SKIP,
            "No A0 baseline records found",
        )
    judged = [r for r in baseline if r.get("correct_by_judge") is not None]
    if not judged:
        return CheckResult(
            "check_baseline_plausibility",
            CheckStatus.SKIP,
            "Baseline records have no judge labels",
        )
    accuracy = sum(1 for r in judged if r["correct_by_judge"]) / len(judged)
    lo, hi = expected_range
    evidence = {
        "accuracy": accuracy,
        "expected_range": list(expected_range),
        "n_baseline": len(judged),
    }
    if accuracy < lo or accuracy > hi:
        direction = "below" if accuracy < lo else "above"
        return CheckResult(
            "check_baseline_plausibility",
            CheckStatus.WARN,
            (
                f"C0 baseline accuracy {accuracy * 100:.2f}% is {direction} "
                f"expected range ({lo * 100:.1f}%–{hi * 100:.1f}%)"
            ),
            evidence=evidence,
        )
    return CheckResult(
        "check_baseline_plausibility",
        CheckStatus.PASS,
        (
            f"C0 baseline accuracy {accuracy * 100:.2f}% within "
            f"expected range ({lo * 100:.1f}%–{hi * 100:.1f}%)"
        ),
        evidence=evidence,
    )


def check_help_hurt_ratio_reasonable(
    records: list[dict],
    min: float = 0.2,
    max: float = 5.0,
) -> CheckResult:
    """Check the aggregate help/hurt ratio for non-A0 approaches is plausible.

    *helped* = item where approach was correct but A0 was wrong.
    *hurt*   = item where approach was wrong but A0 was correct.
    """
    # Build per-item lookup: item_id → approach_id → correct
    item_map: dict[str, dict[str, bool]] = {}
    for r in records:
        iid = r.get("item_id", "")
        aid = r.get("approach_id", "")
        correct = bool(r.get("correct_by_judge", False))
        item_map.setdefault(iid, {})[aid] = correct

    helped = hurt = 0
    non_baseline_seen = False

    for _, approaches in item_map.items():
        c0_correct = approaches.get("A0", False)
        for aid, correct in approaches.items():
            if aid == "A0":
                continue
            non_baseline_seen = True
            if correct and not c0_correct:
                helped += 1
            elif not correct and c0_correct:
                hurt += 1

    if not non_baseline_seen:
        return CheckResult(
            "check_help_hurt_ratio_reasonable",
            CheckStatus.SKIP,
            "No non-baseline (non-A0) approaches found",
        )

    evidence: dict[str, Any] = {"helped": helped, "hurt": hurt}

    if helped == 0 and hurt == 0:
        return CheckResult(
            "check_help_hurt_ratio_reasonable",
            CheckStatus.PASS,
            "No help/hurt differential observed (all approaches neutral vs C0)",
            evidence=evidence,
        )

    if hurt == 0:
        return CheckResult(
            "check_help_hurt_ratio_reasonable",
            CheckStatus.WARN,
            f"Approach only helps, never hurts ({helped} helped, 0 hurt) — suspicious",
            evidence=evidence,
        )

    ratio = helped / hurt
    evidence["ratio"] = ratio

    if ratio < min or ratio > max:
        return CheckResult(
            "check_help_hurt_ratio_reasonable",
            CheckStatus.WARN,
            (
                f"Help/hurt ratio {ratio:.2f} outside expected range "
                f"({min:.1f}–{max:.1f}); helped={helped}, hurt={hurt}"
            ),
            evidence=evidence,
        )
    return CheckResult(
        "check_help_hurt_ratio_reasonable",
        CheckStatus.PASS,
        f"Help/hurt ratio {ratio:.2f} within expected range; helped={helped}, hurt={hurt}",
        evidence=evidence,
    )
