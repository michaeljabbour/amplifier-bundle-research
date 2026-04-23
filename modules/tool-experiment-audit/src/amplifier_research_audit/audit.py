"""
audit.py — Main audit orchestration.

``audit_experiment`` is the primary entry point.  It loads JSONL records and
an optional manifest from an experiment directory, runs every check in the
integrity contract, computes an overall verdict, and returns a rich
``AuditResult``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .checklist import (
    CheckResult,
    CheckStatus,
    IntegrityContract,
    check_baseline_plausibility,
    check_handler_error_rate,
    check_help_hurt_ratio_reasonable,
    check_judge_coverage,
    check_judge_distribution,
    check_manifest_fields,
    check_manifest_present,
    check_no_duplicate_responses,
    check_response_length_distribution,
    check_row_count,
    is_error_response,
)

# ---------------------------------------------------------------------------
# Verdict enum
# ---------------------------------------------------------------------------


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SUSPICIOUS = "SUSPICIOUS"


# ---------------------------------------------------------------------------
# AuditResult
# ---------------------------------------------------------------------------


@dataclass
class AuditResult:
    """Full result of auditing a single experiment directory."""

    experiment_dir: Path
    experiment_name: str
    verdict: Verdict
    checks: list[CheckResult]
    records_count: int
    handler_error_rate: float
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def load_records(experiment_dir: Path) -> list[dict]:
    """Load all JSONL records from *results.jsonl* in *experiment_dir*.

    Returns an empty list if the file is absent or unreadable.
    """
    results_file = experiment_dir / "results.jsonl"
    if not results_file.exists():
        return []
    records: list[dict] = []
    with results_file.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # skip malformed lines
    return records


def load_manifest(experiment_dir: Path) -> dict | None:
    """Load *manifest.json* or *experiment_meta.json* from *experiment_dir*.

    Returns ``None`` when neither file is present or is unreadable.
    """
    for name in ("manifest.json", "experiment_meta.json"):
        path = experiment_dir / name
        if path.exists():
            try:
                with path.open(encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                pass
    return None


def compute_verdict(checks: list[CheckResult]) -> Verdict:
    """Aggregate per-check statuses into a single overall verdict.

    Rules:
    - Any FAIL  → FAIL
    - Any WARN (no FAIL) → SUSPICIOUS
    - All PASS / SKIP   → PASS
    """
    statuses = {c.status for c in checks}
    if CheckStatus.FAIL in statuses:
        return Verdict.FAIL
    if CheckStatus.WARN in statuses:
        return Verdict.SUSPICIOUS
    return Verdict.PASS


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def audit_experiment(
    experiment_dir: Path,
    expected_n_items: int | None = None,
    contract: IntegrityContract | None = None,
) -> AuditResult:
    """Audit a single experiment directory against the integrity contract.

    Args:
        experiment_dir: Path to the experiment (must contain ``results.jsonl``).
        expected_n_items: When provided, the row-count check is run with this
            as the expected item count.  The expected approach count is inferred
            from the data.
        contract: Configuration for all thresholds.  Uses sensible defaults
            when ``None``.

    Returns:
        AuditResult with overall verdict (PASS / FAIL / SUSPICIOUS) and full
        per-check detail.
    """
    # Resolve defaults once so pyright sees a non-optional type downstream.
    _c: IntegrityContract = contract if contract is not None else IntegrityContract()

    experiment_dir = Path(experiment_dir)
    records = load_records(experiment_dir)
    manifest = load_manifest(experiment_dir)

    checks: list[CheckResult] = []
    notes: list[str] = []

    # Guard: no results.jsonl is itself a hard failure
    if not records:
        results_path = experiment_dir / "results.jsonl"
        if not results_path.exists():
            notes.append("results.jsonl not found — cannot audit record-level checks")
        else:
            notes.append("results.jsonl is empty")
        checks.append(
            CheckResult(
                "check_row_count",
                CheckStatus.FAIL,
                "No results.jsonl found or file is empty",
                evidence={"actual": 0, "expected": "?"},
            )
        )
    else:
        # ----------------------------------------------------------------
        # 1. Completeness
        # ----------------------------------------------------------------
        if expected_n_items is not None:
            n_approaches = len({r.get("approach_id") for r in records})
            checks.append(check_row_count(records, expected_n_items, n_approaches))

        checks.append(check_handler_error_rate(records, _c.handler_error_threshold))

        # ----------------------------------------------------------------
        # 2. Response sanity
        # ----------------------------------------------------------------
        checks.append(
            check_response_length_distribution(
                records,
                _c.min_response_median_chars,
                _c.max_short_response_fraction,
                _c.short_response_chars,
            )
        )
        checks.append(check_no_duplicate_responses(records, _c.max_duplicate_fraction))

        # ----------------------------------------------------------------
        # 3. Judge integrity
        # ----------------------------------------------------------------
        checks.append(check_judge_coverage(records))
        checks.append(check_judge_distribution(records, _c.warn_if_accuracy_below))

        # ----------------------------------------------------------------
        # 5. Statistical sanity
        # ----------------------------------------------------------------
        checks.append(check_baseline_plausibility(records, _c.baseline_expected_range))
        checks.append(
            check_help_hurt_ratio_reasonable(
                records,
                _c.help_hurt_ratio_min,
                _c.help_hurt_ratio_max,
            )
        )

    # ----------------------------------------------------------------
    # 4. Provenance (always run, even when records are absent)
    # ----------------------------------------------------------------
    checks.append(check_manifest_present(experiment_dir))
    if manifest is not None:
        checks.append(check_manifest_fields(manifest, _c.manifest_required_fields))

    # Compute raw handler-error rate for summary display
    error_count = sum(1 for r in records if is_error_response(r.get("response", "")))
    handler_error_rate = error_count / len(records) if records else 0.0

    return AuditResult(
        experiment_dir=experiment_dir,
        experiment_name=experiment_dir.name,
        verdict=compute_verdict(checks),
        checks=checks,
        records_count=len(records),
        handler_error_rate=handler_error_rate,
        notes=notes,
    )
