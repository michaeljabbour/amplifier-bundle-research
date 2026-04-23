"""
Tests for report.py — TDD RED phase.

Covers Test 7: report markdown structure contains required sections.
"""

from pathlib import Path

from amplifier_research_audit.audit import AuditResult, Verdict
from amplifier_research_audit.checklist import CheckResult, CheckStatus
from amplifier_research_audit.report import generate_batch_report, generate_report

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "A" * 300


def make_minimal_audit_result(
    experiment_name: str = "test_exp",
    verdict: Verdict = Verdict.PASS,
    extra_checks: list | None = None,
) -> AuditResult:
    checks = [
        CheckResult("check_handler_error_rate", CheckStatus.PASS, "0.0% (threshold 5.0%)"),
        CheckResult("check_response_length_distribution", CheckStatus.PASS, "Median 300 chars"),
        CheckResult("check_no_duplicate_responses", CheckStatus.PASS, "0.0% duplicates"),
        CheckResult("check_judge_coverage", CheckStatus.PASS, "All records populated"),
        CheckResult("check_judge_distribution", CheckStatus.PASS, "Accuracy 10.0%"),
        CheckResult("check_manifest_present", CheckStatus.FAIL, "No manifest found"),
        CheckResult("check_baseline_plausibility", CheckStatus.PASS, "Accuracy 10.0% in range"),
        CheckResult(
            "check_help_hurt_ratio_reasonable", CheckStatus.SKIP, "No non-baseline approaches"
        ),
    ]
    if extra_checks:
        checks.extend(extra_checks)
    return AuditResult(
        experiment_dir=Path(f"/tmp/{experiment_name}"),
        experiment_name=experiment_name,
        verdict=verdict,
        checks=checks,
        records_count=40,
        handler_error_rate=0.0,
    )


def make_fail_result(experiment_name: str = "failed_exp") -> AuditResult:
    checks = [
        CheckResult(
            "check_handler_error_rate",
            CheckStatus.FAIL,
            "89.0% (threshold 5.0%)",
            evidence={"rate": 0.89, "threshold": 0.05, "count": 89},
        ),
    ]
    return AuditResult(
        experiment_dir=Path(f"/tmp/{experiment_name}"),
        experiment_name=experiment_name,
        verdict=Verdict.FAIL,
        checks=checks,
        records_count=100,
        handler_error_rate=0.89,
    )


# ---------------------------------------------------------------------------
# Test 7: report markdown structure
# ---------------------------------------------------------------------------


class TestReportMarkdownStructure:
    def test_report_has_title(self):
        result = make_minimal_audit_result("my_experiment")
        report = generate_report(result)
        assert "my_experiment" in report
        assert "# " in report  # has a markdown heading

    def test_report_has_verdict_line(self):
        """Report must have a bold Verdict line with emoji."""
        result = make_minimal_audit_result(verdict=Verdict.PASS)
        report = generate_report(result)
        assert "Verdict" in report
        assert "PASS" in report

    def test_fail_verdict_shows_fail_emoji_or_label(self):
        result = make_fail_result()
        report = generate_report(result)
        assert "FAIL" in report
        assert "❌" in report or "FAIL" in report

    def test_suspicious_verdict_shows_warn_emoji_or_label(self):
        result = make_minimal_audit_result(
            verdict=Verdict.SUSPICIOUS,
            extra_checks=[
                CheckResult(
                    "check_baseline_plausibility",
                    CheckStatus.WARN,
                    "0.3% below expected range",
                )
            ],
        )
        report = generate_report(result)
        assert "SUSPICIOUS" in report or "⚠" in report

    def test_report_has_summary_section(self):
        result = make_minimal_audit_result()
        report = generate_report(result)
        assert "## Summary" in report or "## Check" in report

    def test_report_shows_total_records(self):
        result = make_minimal_audit_result()
        report = generate_report(result)
        # Should show record count somewhere
        assert "40" in report

    def test_report_has_check_details_section(self):
        result = make_minimal_audit_result()
        report = generate_report(result)
        # Check details must be present
        assert "check_handler_error_rate" in report or "handler_error" in report.lower()

    def test_report_shows_pass_fail_checkmarks(self):
        """✅ for PASS, ❌ for FAIL checks."""
        result = make_fail_result()
        report = generate_report(result)
        assert "❌" in report

    def test_report_has_recommendations_section(self):
        result = make_fail_result()
        report = generate_report(result)
        assert "Recommendation" in report

    def test_report_shows_handler_error_rate(self):
        result = make_fail_result()
        report = generate_report(result)
        assert "89" in report  # error rate visible

    def test_report_shows_passing_checks_fraction(self):
        """Summary should include 'A/B' passing checks count."""
        result = make_minimal_audit_result()
        report = generate_report(result)
        # Should have some fraction notation or counts
        assert "/" in report  # e.g. "7/8 checks passed"

    def test_fail_report_shows_evidence(self):
        """FAIL check result includes evidence in the report."""
        result = make_fail_result()
        report = generate_report(result)
        # Evidence: rate=0.89 should appear
        assert "89" in report


class TestBatchReport:
    def test_batch_report_has_title(self):
        results = [
            make_minimal_audit_result("exp_one", Verdict.PASS),
            make_fail_result("exp_two"),
        ]
        report = generate_batch_report(results)
        assert "Batch" in report or "Audit" in report

    def test_batch_report_includes_all_experiments(self):
        results = [
            make_minimal_audit_result("exp_alpha"),
            make_minimal_audit_result("exp_beta"),
            make_fail_result("exp_gamma"),
        ]
        report = generate_batch_report(results)
        assert "exp_alpha" in report
        assert "exp_beta" in report
        assert "exp_gamma" in report

    def test_batch_report_has_summary_table_or_list(self):
        """Batch report should include a per-experiment summary."""
        results = [
            make_minimal_audit_result("a", Verdict.PASS),
            make_fail_result("b"),
        ]
        report = generate_batch_report(results)
        # Should show verdicts for each
        assert "PASS" in report
        assert "FAIL" in report

    def test_batch_report_with_single_experiment(self):
        results = [make_minimal_audit_result("solo")]
        report = generate_batch_report(results)
        assert "solo" in report

    def test_batch_report_with_empty_list(self):
        report = generate_batch_report([])
        assert isinstance(report, str)
        assert len(report) > 0  # should not crash
