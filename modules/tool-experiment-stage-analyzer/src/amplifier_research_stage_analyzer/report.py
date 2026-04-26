"""
report.py — Markdown report generation for stage-trace analysis.

Public API:
    generate_report(analysis: dict, output_path: str | None = None) -> str
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_CATEGORY_LABELS: dict[str, str] = {
    "gen_substantive_critic_empty": "Generator Substantive + Critic Empty",
    "gen_substantive_critic_substantive": "Generator Substantive + Critic Substantive",
    "gen_empty_critic_substantive": "Generator Empty + Critic Substantive",
    "gen_empty_critic_empty": "Both Empty",
    "gen_substantive_no_critic": "Generator Substantive (No Critic — A0 anomaly)",
    "unknown": "Unknown / Schema Gap",
}

_CATEGORY_NOTES: dict[str, str] = {
    "gen_substantive_critic_empty": "H1b evidence: critic is the failure mode",
    "gen_substantive_critic_substantive": "H1a evidence: revert decision is the failure mode",
    "gen_empty_critic_substantive": "Revert preserved a generator empty output",
    "gen_empty_critic_empty": "Both generator and critic stages failed",
    "gen_substantive_no_critic": "Anomaly: A0-style record, non-empty generator, final empty",
    "unknown": "Schema gaps or unclassifiable records",
}


def _pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A"
    return f"{numerator / denominator * 100:.1f}%"


def _fmt_fraction(f: float) -> str:
    return f"{f:.3f} ({f * 100:.1f}%)"


def _verdict_emoji(confirmed: bool) -> str:
    return "✅ CONFIRMED" if confirmed else "❌ NOT CONFIRMED"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_report(analysis: dict, output_path: str | None = None) -> str:
    """Generate a Markdown stage-analysis report.

    Args:
        analysis: Combined analysis dict as produced by the CLI or programmatic
            pipeline.  Must have keys:
            ``categorize`` (with ``counts`` and ``records``),
            ``hypothesis`` (from
            :func:`~amplifier_research_stage_analyzer.analyze.test_h1_hypotheses`),
            ``total_records``, and ``total_empty``.
        output_path: If provided, write the report to this file path.

    Returns:
        Markdown string.

    Example:
        >>> md = generate_report(analysis)
        >>> print(md[:100])
        # Stage-Trace Empty-Response Analysis Report
    """
    cat_result = analysis["categorize"]
    hyp = analysis["hypothesis"]
    counts = cat_result["counts"]
    total_records = analysis["total_records"]
    total_empty = analysis["total_empty"]

    lines: list[str] = []

    # Header
    lines.append("# Stage-Trace Empty-Response Analysis Report")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total records ingested:** {total_records}")
    lines.append(
        f"- **Total empty-final records:** {total_empty} "
        f"({_pct(total_empty, total_records)} of all records)"
    )
    lines.append("")
    lines.append(
        "Empty-final records are those where `final_is_empty == True`. "
        "Each is classified into one of six failure-mode categories below."
    )
    lines.append("")

    # Categories
    lines.append("## Categories")
    lines.append("")
    lines.append("| Category | Count | % of Empties | Note |")
    lines.append("|---|---|---|---|")
    for cat in [
        "gen_substantive_critic_empty",
        "gen_substantive_critic_substantive",
        "gen_empty_critic_substantive",
        "gen_empty_critic_empty",
        "gen_substantive_no_critic",
        "unknown",
    ]:
        n = counts.get(cat, 0)
        label = _CATEGORY_LABELS.get(cat, cat)
        note = _CATEGORY_NOTES.get(cat, "")
        lines.append(f"| {label} | {n} | {_pct(n, total_empty)} | {note} |")
    lines.append("")

    # Hypothesis Tests
    lines.append("## Hypothesis Tests (Pre-Registered Criteria §2.3)")
    lines.append("")

    # H1a
    lines.append("### H1a — Reflection stage is the failure source")
    lines.append("")
    lines.append(
        "> **Confirmed if:** "
        "(gen_substantive_critic_substantive + gen_substantive_critic_empty) "
        "/ total_empties ≥ 0.40"
    )
    lines.append("")
    h1a_n = counts.get("gen_substantive_critic_empty", 0) + counts.get(
        "gen_substantive_critic_substantive", 0
    )
    lines.append(
        f"- Supporting records: {h1a_n} / {total_empty} empties = "
        f"{_fmt_fraction(hyp['h1a_fraction'])}"
    )
    lines.append(f"- **Verdict: {_verdict_emoji(hyp['h1a_confirmed'])}**")
    lines.append("")

    # H1b
    lines.append("### H1b — Critic empty output is the proximate cause")
    lines.append("")
    lines.append("> **Confirmed if:** gen_substantive_critic_empty / total_empties ≥ 0.40")
    lines.append("")
    h1b_n = counts.get("gen_substantive_critic_empty", 0)
    lines.append(
        f"- Supporting records: {h1b_n} / {total_empty} empties = "
        f"{_fmt_fraction(hyp['h1b_fraction'])}"
    )
    lines.append(f"- **Verdict: {_verdict_emoji(hyp['h1b_confirmed'])}**")
    lines.append("")

    # Evidence
    evidence = hyp.get("evidence", [])
    if evidence:
        lines.append("### Evidence Records")
        lines.append("")
        lines.append(
            f"{len(evidence)} record(s) from confirming categories (showing up to 10 item_ids):"
        )
        lines.append("")
        for ev in evidence[:10]:
            lines.append(f"- `{ev.get('item_id', '<unknown>')}`")
        if len(evidence) > 10:
            lines.append(f"- *(... and {len(evidence) - 10} more)*")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Generated by `amplifier-research-stage-analyzer`. "
        "Threshold: 0.40 per reflection-tokens pre-registration §2.3.*"
    )

    report_text = "\n".join(lines)

    if output_path is not None:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_text, encoding="utf-8")

    return report_text
