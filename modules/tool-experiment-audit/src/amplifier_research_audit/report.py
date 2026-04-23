"""
report.py — Markdown report generator.

``generate_report``  → Markdown string for a single AuditResult.
``generate_batch_report`` → Markdown string for a list of AuditResults.
"""

from __future__ import annotations

from .audit import AuditResult, Verdict
from .checklist import CheckResult, CheckStatus

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_STATUS_EMOJI = {
    CheckStatus.PASS: "✅",
    CheckStatus.FAIL: "❌",
    CheckStatus.WARN: "⚠️",
    CheckStatus.SKIP: "⏭️",
}

_VERDICT_EMOJI = {
    Verdict.PASS: "✅",
    Verdict.FAIL: "❌",
    Verdict.SUSPICIOUS: "⚠️",
}

_CHECK_CATEGORIES: dict[str, str] = {
    "check_row_count": "Completeness",
    "check_handler_error_rate": "Completeness",
    "check_response_length_distribution": "Response Sanity",
    "check_no_duplicate_responses": "Response Sanity",
    "check_judge_coverage": "Judge Integrity",
    "check_judge_distribution": "Judge Integrity",
    "check_manifest_present": "Provenance",
    "check_manifest_fields": "Provenance",
    "check_baseline_plausibility": "Statistical Sanity",
    "check_help_hurt_ratio_reasonable": "Statistical Sanity",
}

_CATEGORY_ORDER = [
    "Completeness",
    "Response Sanity",
    "Judge Integrity",
    "Provenance",
    "Statistical Sanity",
]


def _categorise(checks: list[CheckResult]) -> dict[str, list[CheckResult]]:
    grouped: dict[str, list[CheckResult]] = {cat: [] for cat in _CATEGORY_ORDER}
    grouped.setdefault("Other", [])
    for chk in checks:
        cat = _CHECK_CATEGORIES.get(chk.name, "Other")
        grouped.setdefault(cat, []).append(chk)
    return {k: v for k, v in grouped.items() if v}


def _format_check_line(chk: CheckResult) -> str:
    emoji = _STATUS_EMOJI.get(chk.status, "❓")
    line = f"- {emoji} **{chk.name}**: {chk.message}"
    # Append key evidence for FAIL / WARN
    if chk.status in (CheckStatus.FAIL, CheckStatus.WARN) and chk.evidence:
        ev_parts = []
        for k, v in chk.evidence.items():
            if k in ("threshold", "rate", "missing", "accuracy", "ratio", "short_fraction"):
                if isinstance(v, float):
                    ev_parts.append(f"{k}={v:.4f}")
                else:
                    ev_parts.append(f"{k}={v!r}")
        if ev_parts:
            line += f"  \n  *Evidence: {', '.join(ev_parts)}*"
    return line


def _recommendations(result: AuditResult) -> list[str]:
    recs: list[str] = []
    fail_names = {c.name for c in result.checks if c.status == CheckStatus.FAIL}
    warn_names = {c.name for c in result.checks if c.status == CheckStatus.WARN}

    if "check_handler_error_rate" in fail_names:
        rate_pct = result.handler_error_rate * 100
        recs.append(
            f"Pipeline produced {rate_pct:.1f}% error responses — "
            "re-run with a fixed pipeline before trusting any downstream analysis."
        )
    if "check_row_count" in fail_names:
        recs.append(
            "Record count mismatch — verify no items were skipped or duplicated during execution."
        )
    if "check_response_length_distribution" in fail_names:
        recs.append(
            "Many responses are suspiciously short "
            "— inspect raw responses for truncation or empty outputs."
        )
    if "check_no_duplicate_responses" in fail_names:
        recs.append(
            "High duplicate response fraction detected — check for stuck/cached generators."
        )
    if "check_judge_coverage" in fail_names:
        recs.append(
            "Some records are missing judge labels "
            "— ensure the judge pipeline completed successfully."
        )
    if "check_manifest_present" in fail_names:
        recs.append(
            "No manifest.json found "
            "— add manifest with judge_model, split_sha256, and execution_seed "
            "before treating results as reproducible."
        )
    if "check_manifest_fields" in fail_names:
        recs.append(
            "Manifest is incomplete "
            "— add all required fields (judge_model, split_sha256, execution_seed)."
        )
    if "check_baseline_plausibility" in warn_names:
        recs.append(
            "C0 baseline accuracy is outside expected range — "
            "verify the data split and baseline prompt are correct."
        )
    if "check_judge_distribution" in warn_names:
        recs.append("Near-zero overall accuracy — confirm judge labeling is functioning correctly.")
    if not recs:
        recs.append(
            "No critical issues detected.  Review any warnings above before publishing results."
        )
    return recs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_report(result: AuditResult) -> str:
    """Return a Markdown audit report for a single experiment."""
    lines: list[str] = []
    verdict_emoji = _VERDICT_EMOJI.get(result.verdict, "❓")

    lines.append(f"# Experiment Audit Report: {result.experiment_name}")
    lines.append("")
    lines.append(f"**Verdict:** {verdict_emoji} {result.verdict.value}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total records:** {result.records_count}")
    lines.append(f"- **HANDLER_ERROR rate:** {result.handler_error_rate * 100:.1f}%")

    passing = sum(1 for c in result.checks if c.status == CheckStatus.PASS)
    total = len(result.checks)
    lines.append(f"- **Passing checks:** {passing}/{total}")

    if result.notes:
        for note in result.notes:
            lines.append(f"- ⚠️ {note}")
    lines.append("")

    # Check details by category
    lines.append("## Check Details")
    grouped = _categorise(result.checks)
    for category, checks in grouped.items():
        lines.append("")
        lines.append(f"### {category}")
        for chk in checks:
            lines.append(_format_check_line(chk))
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    for rec in _recommendations(result):
        lines.append(f"- {rec}")
    lines.append("")

    return "\n".join(lines)


def generate_batch_report(results: list[AuditResult]) -> str:
    """Return a consolidated Markdown audit report covering multiple experiments."""
    lines: list[str] = []
    lines.append("# Batch Experiment Audit Report")
    lines.append("")

    if not results:
        lines.append("*No experiments found.*")
        lines.append("")
        return "\n".join(lines)

    # Summary table
    lines.append("## Summary")
    lines.append("")
    pass_count = sum(1 for r in results if r.verdict == Verdict.PASS)
    suspicious_count = sum(1 for r in results if r.verdict == Verdict.SUSPICIOUS)
    fail_count = sum(1 for r in results if r.verdict == Verdict.FAIL)

    lines.append(
        f"Audited **{len(results)}** experiments: "
        f"✅ {pass_count} PASS, "
        f"⚠️ {suspicious_count} SUSPICIOUS, "
        f"❌ {fail_count} FAIL"
    )
    lines.append("")
    lines.append("| Experiment | Records | Error Rate | Verdict |")
    lines.append("|---|---|---|---|")
    for r in results:
        emoji = _VERDICT_EMOJI.get(r.verdict, "❓")
        lines.append(
            f"| `{r.experiment_name}` "
            f"| {r.records_count} "
            f"| {r.handler_error_rate * 100:.1f}% "
            f"| {emoji} {r.verdict.value} |"
        )
    lines.append("")

    # Per-experiment detail
    lines.append("---")
    lines.append("")
    for r in results:
        lines.append(generate_report(r))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
