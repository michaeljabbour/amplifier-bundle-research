"""
TDD RED phase — test_report.py

Tests for report.py: Markdown report generation.
All tests MUST FAIL before implementation exists.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_ALL_CATEGORIES = [
    "gen_substantive_critic_empty",
    "gen_substantive_critic_substantive",
    "gen_empty_critic_substantive",
    "gen_empty_critic_empty",
    "gen_substantive_no_critic",
    "unknown",
]


def _make_analysis_result(
    gen_sub_crit_empty: int = 3,
    gen_sub_crit_sub: int = 2,
    gen_empty_crit_empty: int = 5,
    gen_empty_crit_sub: int = 0,
    gen_sub_no_critic: int = 0,
    unknown: int = 0,
    h1a_confirmed: bool = True,
    h1a_fraction: float = 0.50,
    h1b_confirmed: bool = False,
    h1b_fraction: float = 0.30,
) -> dict:
    """Build a synthetic combined analysis dict for report generation."""
    counts = {
        "gen_substantive_critic_empty": gen_sub_crit_empty,
        "gen_substantive_critic_substantive": gen_sub_crit_sub,
        "gen_empty_critic_substantive": gen_empty_crit_sub,
        "gen_empty_critic_empty": gen_empty_crit_empty,
        "gen_substantive_no_critic": gen_sub_no_critic,
        "unknown": unknown,
    }
    records: dict = {cat: [] for cat in _ALL_CATEGORIES}

    hypothesis = {
        "h1a_confirmed": h1a_confirmed,
        "h1a_fraction": h1a_fraction,
        "h1b_confirmed": h1b_confirmed,
        "h1b_fraction": h1b_fraction,
        "evidence": [{"item_id": "ev_001"}, {"item_id": "ev_002"}],
    }
    return {
        "categorize": {"counts": counts, "records": records},
        "hypothesis": hypothesis,
        "total_records": 15,
        "total_empty": gen_sub_crit_empty + gen_sub_crit_sub + gen_empty_crit_sub + gen_empty_crit_empty + gen_sub_no_critic + unknown,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_report_has_required_sections() -> None:
    """Generated Markdown report must contain Summary, Categories, H1a, H1b sections."""
    from amplifier_research_stage_analyzer.report import generate_report

    analysis = _make_analysis_result()
    report_text = generate_report(analysis)

    assert isinstance(report_text, str), "generate_report must return a string"
    assert "Summary" in report_text, "Report must contain 'Summary' section"
    assert "Categories" in report_text, "Report must contain 'Categories' section"
    assert "H1a" in report_text, "Report must contain 'H1a' section or label"
    assert "H1b" in report_text, "Report must contain 'H1b' section or label"


def test_report_includes_counts_and_percentages() -> None:
    """Numerical claims in the report match the input data."""
    from amplifier_research_stage_analyzer.report import generate_report

    analysis = _make_analysis_result(
        gen_sub_crit_empty=4,
        gen_sub_crit_sub=2,
        gen_empty_crit_empty=4,
        h1a_fraction=0.60,
        h1b_fraction=0.40,
    )
    report_text = generate_report(analysis)

    # The category counts should appear in the report
    assert "4" in report_text, "Report should include count '4' for gen_sub_crit_empty"
    assert "2" in report_text, "Report should include count '2' for gen_sub_crit_sub"

    # H1a and H1b fractions (as percentages) should appear
    # h1a_fraction=0.60 → "60" should appear
    # h1b_fraction=0.40 → "40" should appear
    assert "60" in report_text or "0.60" in report_text, (
        "Report should include H1a fraction 0.60 or 60%"
    )
    assert "40" in report_text or "0.40" in report_text, (
        "Report should include H1b fraction 0.40 or 40%"
    )


def test_report_shows_confirmed_verdict() -> None:
    """Report must clearly label a confirmed hypothesis as CONFIRMED."""
    from amplifier_research_stage_analyzer.report import generate_report

    analysis = _make_analysis_result(h1a_confirmed=True, h1b_confirmed=True)
    report_text = generate_report(analysis)

    confirmed_keywords = ["confirmed", "CONFIRMED", "✅", "True"]
    found_any = any(kw in report_text for kw in confirmed_keywords)
    assert found_any, (
        f"Report should indicate confirmed status. Got:\n{report_text[:500]}"
    )


def test_report_shows_not_confirmed_verdict() -> None:
    """Report must clearly label an unconfirmed hypothesis as NOT CONFIRMED or similar."""
    from amplifier_research_stage_analyzer.report import generate_report

    analysis = _make_analysis_result(h1a_confirmed=False, h1b_confirmed=False)
    report_text = generate_report(analysis)

    not_confirmed_keywords = [
        "not confirmed", "NOT CONFIRMED", "Not confirmed",
        "❌", "False", "not met", "NOT MET",
    ]
    found_any = any(kw in report_text for kw in not_confirmed_keywords)
    assert found_any, (
        f"Report should indicate not-confirmed status. Got:\n{report_text[:500]}"
    )


def test_report_writes_to_file(tmp_path) -> None:
    """generate_report can write to a file path when output_path is provided."""
    from amplifier_research_stage_analyzer.report import generate_report

    analysis = _make_analysis_result()
    output_file = tmp_path / "stage_analysis.md"

    generate_report(analysis, output_path=str(output_file))

    assert output_file.exists(), f"Expected output file at {output_file}"
    content = output_file.read_text()
    assert "Summary" in content
    assert len(content) > 100, "Output file should have substantial content"
