"""
TDD RED phase — test_report.py

Tests for report.py: generate Markdown provenance reports.
These tests import from amplifier_research_provenance_check.report,
which does NOT exist yet.  All tests must FAIL on first run.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_report_summary_counts() -> None:
    """Summary section contains accurate counts for each status."""
    from amplifier_research_provenance_check.git_check import FileStatus
    from amplifier_research_provenance_check.report import generate_report

    results = {
        "data/tracked_a.json": FileStatus.TRACKED,
        "data/tracked_b.json": FileStatus.TRACKED,
        "data/untracked.json": FileStatus.UNTRACKED,
        "data/missing.json": FileStatus.MISSING,
    }
    report = generate_report(results)

    assert "2" in report, "Expected count 2 (TRACKED) in report"
    assert "1" in report, "Expected count 1 (UNTRACKED) in report"
    assert "TRACKED" in report
    assert "UNTRACKED" in report
    assert "MISSING" in report
    # Spot-check that all four paths appear somewhere in the report
    for path in results:
        assert path in report, f"Expected path '{path}' in report"


def test_report_lists_untracked_with_paths() -> None:
    """UNTRACKED files appear explicitly in the report body."""
    from amplifier_research_provenance_check.git_check import FileStatus
    from amplifier_research_provenance_check.report import generate_report

    results = {
        "data/tracked.json": FileStatus.TRACKED,
        "data/untracked_artifact.json": FileStatus.UNTRACKED,
        "data/another_untracked.jsonl": FileStatus.UNTRACKED,
    }
    report = generate_report(results)

    assert "data/untracked_artifact.json" in report
    assert "data/another_untracked.jsonl" in report
    # Untracked section should be clearly labeled
    assert "UNTRACKED" in report


def test_report_includes_recommendations() -> None:
    """Non-empty recommendations appear when UNTRACKED files are present."""
    from amplifier_research_provenance_check.git_check import FileStatus
    from amplifier_research_provenance_check.report import generate_report

    results = {
        "data/tracked.json": FileStatus.TRACKED,
        "data/critical_missing.json": FileStatus.UNTRACKED,
    }
    report = generate_report(results)

    # Recommendations section must exist
    assert "Recommendation" in report, "Expected 'Recommendation' section in report"
    # Must suggest git add for the untracked file
    assert "git add" in report, "Expected 'git add' command in recommendations"
    assert "data/critical_missing.json" in report
