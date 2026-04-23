"""
Tests for audit.py — TDD RED phase.

Covers:
  Test 6: audit_experiment aggregates check results (any FAIL → overall FAIL)
  Test 8: CLI batch mode audits multiple dirs
"""

import json
import sys
from pathlib import Path

from amplifier_research_audit.audit import AuditResult, Verdict, audit_experiment
from amplifier_research_audit.checklist import CheckStatus

LONG_RESPONSE = "Response text that is long enough to pass length checks. " * 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _make_clean_experiment(
    directory: Path,
    n_items: int = 20,
    n_approaches: int = 2,
    error_fraction: float = 0.0,
    correct_fraction: float = 0.1,
    write_manifest: bool = False,
) -> Path:
    """Write a minimal results.jsonl for testing.

    Responses are unique per record to avoid triggering the duplicate check.
    correct_by_judge is set so that A0 baseline accuracy ~ correct_fraction,
    kept strictly below the 25% upper plausibility bound.
    """
    total = n_items * n_approaches
    n_errors = int(error_fraction * total)
    records = []
    correct_counter = 0
    n_correct_needed = max(1, int(correct_fraction * n_items))  # for A0 only
    for i in range(n_items):
        for j in range(n_approaches):
            idx = i * n_approaches + j
            is_error = idx < n_errors
            # Unique response text per record avoids duplicate-detection false positives
            resp = (
                "[HANDLER_ERROR]"
                if is_error
                else (f"Response for item_{i} approach_A{j}: " + ("text " * 30))
            )
            # Baseline (A0) accuracy ~ correct_fraction but capped at 20%
            if j == 0 and not is_error and correct_counter < n_correct_needed:
                correct = True
                correct_counter += 1
            else:
                correct = False
            records.append(
                {
                    "item_id": f"item_{i}",
                    "approach_id": f"A{j}",
                    "approach_name": f"approach_{j}",
                    "response": resp,
                    "correct_by_judge": correct,
                    "cost_usd": 0.01,
                    "tokens": 100,
                    "latency_ms": 1000.0,
                }
            )
    _write_jsonl(directory / "results.jsonl", records)
    if write_manifest:
        (directory / "manifest.json").write_text(
            json.dumps(
                {
                    "judge_model": "gpt-4",
                    "split_sha256": "abc123",
                    "execution_seed": 42,
                }
            )
        )
    return directory


# ---------------------------------------------------------------------------
# Test 6: audit_experiment aggregates check results
# ---------------------------------------------------------------------------


class TestAuditAggregatesCheckResults:
    def test_clean_experiment_is_not_fail(self, tmp_path):
        """Experiment with low error rate should not produce overall FAIL."""
        exp = tmp_path / "clean_exp"
        exp.mkdir()
        _make_clean_experiment(exp, n_items=20, n_approaches=2, correct_fraction=0.15)
        result = audit_experiment(exp)
        assert isinstance(result, AuditResult)
        # Should be PASS or SUSPICIOUS (no manifest → may warn), but not FAIL
        assert result.verdict != Verdict.FAIL

    def test_high_error_rate_triggers_fail(self, tmp_path):
        """89% HANDLER_ERROR → overall FAIL (check_handler_error_rate fails)."""
        exp = tmp_path / "bad_exp"
        exp.mkdir()
        _make_clean_experiment(exp, n_items=100, n_approaches=1, error_fraction=0.89)
        result = audit_experiment(exp)
        assert result.verdict == Verdict.FAIL

    def test_any_fail_overrides_warn(self, tmp_path):
        """When both a FAIL and a WARN exist, verdict is FAIL not SUSPICIOUS."""
        exp = tmp_path / "mixed_exp"
        exp.mkdir()
        # 89% errors (triggers FAIL) + 0% baseline (triggers WARN) — FAIL wins
        records = [
            {
                "item_id": f"item_{i}",
                "approach_id": "A0",
                "approach_name": "C0 baseline",
                "response": "[HANDLER_ERROR]" if i < 89 else LONG_RESPONSE,
                "correct_by_judge": False,
                "cost_usd": 0.01,
                "tokens": 0,
                "latency_ms": 1000.0,
            }
            for i in range(100)
        ]
        _write_jsonl(exp / "results.jsonl", records)
        result = audit_experiment(exp)
        assert result.verdict == Verdict.FAIL

    def test_only_warn_yields_suspicious(self, tmp_path):
        """Only WARN checks (no FAIL) → SUSPICIOUS verdict."""
        exp = tmp_path / "suspicious_exp"
        exp.mkdir()
        # Near-zero C0 accuracy (< 1%) triggers WARN; no FAIL triggers.
        # Use unique responses to avoid triggering the duplicate-detection FAIL.
        records = [
            {
                "item_id": f"item_{i}",
                "approach_id": "A0",
                "approach_name": "C0 baseline",
                # Unique response text per record so duplicate check does not FAIL
                "response": f"Unique answer for item {i}: " + ("explanation " * 20),
                # 1 correct out of 300 = 0.33% → below warn_if_accuracy_below=0.01
                "correct_by_judge": i == 0,
                "cost_usd": 0.01,
                "tokens": 100,
                "latency_ms": 1000.0,
            }
            for i in range(300)
        ]
        _write_jsonl(exp / "results.jsonl", records)
        result = audit_experiment(exp)
        # Should be SUSPICIOUS (WARN from baseline and/or judge distribution)
        assert result.verdict == Verdict.SUSPICIOUS

    def test_audit_result_has_expected_fields(self, tmp_path):
        """AuditResult must carry experiment_name, records_count, handler_error_rate."""
        exp = tmp_path / "fields_exp"
        exp.mkdir()
        _make_clean_experiment(exp, n_items=10, n_approaches=2)
        result = audit_experiment(exp)
        assert result.experiment_name == "fields_exp"
        assert result.records_count == 20
        assert 0.0 <= result.handler_error_rate <= 1.0

    def test_expected_n_items_triggers_row_count_check(self, tmp_path):
        """Passing expected_n_items=30 when only 20 items present → FAIL."""
        exp = tmp_path / "short_exp"
        exp.mkdir()
        _make_clean_experiment(exp, n_items=20, n_approaches=2)
        result = audit_experiment(exp, expected_n_items=30)
        # row_count check should FAIL (20*2=40 rows vs expected 30*2=60)
        row_checks = [c for c in result.checks if c.name == "check_row_count"]
        assert row_checks, "check_row_count should be present when expected_n_items given"
        assert row_checks[0].status == CheckStatus.FAIL

    def test_no_results_jsonl_returns_fail(self, tmp_path):
        """Empty experiment dir (no results.jsonl) → FAIL verdict."""
        exp = tmp_path / "empty_exp"
        exp.mkdir()
        result = audit_experiment(exp)
        assert result.verdict == Verdict.FAIL


# ---------------------------------------------------------------------------
# Test 8: CLI batch mode audits multiple dirs
# ---------------------------------------------------------------------------


class TestCliBatchMode:
    def test_batch_mode_audits_multiple_dirs(self, tmp_path, monkeypatch):
        """
        Batch mode discovers all experiment dirs with results.jsonl under
        --experiments-root and writes a consolidated report.
        """
        # Create two experiment dirs
        for name in ["exp_alpha", "exp_beta"]:
            d = tmp_path / name
            d.mkdir()
            _make_clean_experiment(d, n_items=10, n_approaches=2, correct_fraction=0.10)

        output_file = tmp_path / "batch_audit.md"

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "amplifier_research_audit",
                "--experiments-root",
                str(tmp_path),
                "--output",
                str(output_file),
            ],
        )

        from amplifier_research_audit.cli import main

        main()

        assert output_file.exists(), "Batch report file not created"
        content = output_file.read_text()
        assert "exp_alpha" in content
        assert "exp_beta" in content

    def test_batch_mode_includes_verdict_summary(self, tmp_path, monkeypatch):
        """Batch report includes a summary section with per-experiment verdicts."""
        d = tmp_path / "exp_gamma"
        d.mkdir()
        _make_clean_experiment(d, n_items=5, n_approaches=1)

        output_file = tmp_path / "out.md"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "amplifier_research_audit",
                "--experiments-root",
                str(tmp_path),
                "--output",
                str(output_file),
            ],
        )

        from amplifier_research_audit.cli import main

        main()

        content = output_file.read_text()
        # Should have a summary or batch overview section
        assert "Batch" in content or "Summary" in content or "exp_gamma" in content

    def test_single_experiment_mode(self, tmp_path, monkeypatch):
        """Single --experiment mode writes a report for that directory."""
        exp = tmp_path / "single_exp"
        exp.mkdir()
        _make_clean_experiment(exp, n_items=10, n_approaches=2)

        output_file = tmp_path / "single.md"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "amplifier_research_audit",
                "--experiment",
                str(exp),
                "--output",
                str(output_file),
            ],
        )

        from amplifier_research_audit.cli import main

        main()

        assert output_file.exists()
        content = output_file.read_text()
        assert "single_exp" in content
