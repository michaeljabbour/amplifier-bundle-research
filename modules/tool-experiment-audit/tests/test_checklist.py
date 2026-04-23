"""
Tests for checklist.py — TDD RED phase.

Covers tests 1–5 from the specification, plus supporting unit tests for
all individual check functions.
"""

import json

from amplifier_research_audit.checklist import (
    CheckStatus,
    check_baseline_plausibility,
    check_handler_error_rate,
    check_judge_coverage,
    check_judge_distribution,
    check_manifest_fields,
    check_manifest_present,
    check_no_duplicate_responses,
    check_response_length_distribution,
    check_row_count,
)

# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "A" * 300  # well above any length threshold


def make_record(
    item_id: str = "item_0",
    approach_id: str = "A0",
    approach_name: str = "C0 baseline",
    response: str = LONG_RESPONSE,
    correct_by_judge: bool | None = False,
    cost_usd: float = 0.01,
    tokens: int = 100,
    latency_ms: float = 1000.0,
) -> dict:
    return {
        "item_id": item_id,
        "approach_id": approach_id,
        "approach_name": approach_name,
        "response": response,
        "correct_by_judge": correct_by_judge,
        "cost_usd": cost_usd,
        "tokens": tokens,
        "latency_ms": latency_ms,
    }


def make_grid(
    n_items: int,
    n_approaches: int,
    response: str = LONG_RESPONSE,
    correct_by_judge: bool = False,
) -> list[dict]:
    """Create n_items × n_approaches records."""
    return [
        make_record(
            item_id=f"item_{i}",
            approach_id=f"A{j}",
            response=response,
            correct_by_judge=correct_by_judge,
        )
        for i in range(n_items)
        for j in range(n_approaches)
    ]


# ---------------------------------------------------------------------------
# Test 1: check_row_count passes when correct
# ---------------------------------------------------------------------------


def test_check_row_count_passes_when_correct():
    """600 rows (300 items × 2 approaches) → PASS with '600/600' in message."""
    records = make_grid(300, 2)
    result = check_row_count(records, expected_n_items=300, expected_n_approaches=2)
    assert result.status == CheckStatus.PASS
    assert "600/600" in result.message


# ---------------------------------------------------------------------------
# Test 2: check_row_count fails when missing rows
# ---------------------------------------------------------------------------


def test_check_row_count_fails_when_missing():
    """590 rows instead of 600 → FAIL with '590/600' in message."""
    records = make_grid(295, 2)  # 590 rows
    result = check_row_count(records, expected_n_items=300, expected_n_approaches=2)
    assert result.status == CheckStatus.FAIL
    assert "590/600" in result.message


# ---------------------------------------------------------------------------
# Test 3: check_handler_error_rate detects cascade
# ---------------------------------------------------------------------------


def test_check_handler_error_rate_detects_cascade():
    """89% [HANDLER_ERROR] responses → FAIL."""
    n = 100
    records = [
        make_record(response="[HANDLER_ERROR]") if i < 89 else make_record() for i in range(n)
    ]
    result = check_handler_error_rate(records, threshold=0.05)
    assert result.status == CheckStatus.FAIL
    # Rate should be visible in message or evidence
    assert float(result.evidence.get("rate", 0)) > 0.8


def test_check_handler_error_rate_passes_low_rate():
    """1% [HANDLER_ERROR] → PASS."""
    records = [
        make_record(response="[HANDLER_ERROR]") if i < 1 else make_record() for i in range(100)
    ]
    result = check_handler_error_rate(records, threshold=0.05)
    assert result.status == CheckStatus.PASS


def test_check_handler_error_rate_recognises_item_timeout():
    """[ITEM_TIMEOUT] is treated the same as [HANDLER_ERROR]."""
    records = [
        make_record(response="[ITEM_TIMEOUT]") if i < 90 else make_record() for i in range(100)
    ]
    result = check_handler_error_rate(records, threshold=0.05)
    assert result.status == CheckStatus.FAIL


# ---------------------------------------------------------------------------
# Test 4: check_response_length_distribution flags empty responses
# ---------------------------------------------------------------------------


def test_check_response_length_flags_empty_responses():
    """50% empty responses → FAIL (short_fraction >> max_short_fraction=0.05)."""
    n = 100
    records = [make_record(response="" if i < 50 else LONG_RESPONSE) for i in range(n)]
    result = check_response_length_distribution(records, min_median=100, max_short_fraction=0.05)
    assert result.status == CheckStatus.FAIL


def test_check_response_length_passes_normal():
    """Long responses → PASS."""
    records = [make_record(response=LONG_RESPONSE) for _ in range(100)]
    result = check_response_length_distribution(records, min_median=100, max_short_fraction=0.05)
    assert result.status == CheckStatus.PASS


def test_check_response_length_fails_low_median():
    """All responses ≤ 50 chars when min_median=100 → FAIL."""
    records = [make_record(response="A" * 50) for _ in range(100)]
    result = check_response_length_distribution(records, min_median=100, max_short_fraction=0.05)
    assert result.status == CheckStatus.FAIL


# ---------------------------------------------------------------------------
# Test 5: check_baseline_plausibility flags near-zero accuracy → WARN
# ---------------------------------------------------------------------------


def test_check_baseline_plausibility_flags_near_zero():
    """1/300 = 0.33% accuracy for A0 → WARN (below threshold 1%)."""
    records = [
        make_record(
            approach_id="A0",
            correct_by_judge=(i == 0),  # only first record correct
        )
        for i in range(300)
    ]
    result = check_baseline_plausibility(records, expected_range=(0.01, 0.25))
    assert result.status == CheckStatus.WARN


def test_check_baseline_plausibility_passes_normal():
    """10% accuracy → PASS."""
    records = [make_record(approach_id="A0", correct_by_judge=(i % 10 == 0)) for i in range(100)]
    result = check_baseline_plausibility(records, expected_range=(0.01, 0.25))
    assert result.status == CheckStatus.PASS


def test_check_baseline_plausibility_skips_no_baseline():
    """No A0 records → SKIP."""
    records = [make_record(approach_id="A1") for _ in range(50)]
    result = check_baseline_plausibility(records, expected_range=(0.01, 0.25))
    assert result.status == CheckStatus.SKIP


# ---------------------------------------------------------------------------
# Supporting unit tests for remaining check functions
# ---------------------------------------------------------------------------


class TestCheckJudgeCoverage:
    def test_all_populated_pass(self):
        records = [make_record(correct_by_judge=True) for _ in range(10)]
        assert check_judge_coverage(records).status == CheckStatus.PASS

    def test_some_none_fail(self):
        records = [make_record(correct_by_judge=None) for _ in range(5)]
        assert check_judge_coverage(records).status == CheckStatus.FAIL

    def test_mix_true_false_pass(self):
        records = [make_record(correct_by_judge=b) for b in [True, False, True, False]]
        assert check_judge_coverage(records).status == CheckStatus.PASS


class TestCheckJudgeDistribution:
    def test_normal_accuracy_pass(self):
        records = [make_record(correct_by_judge=(i % 5 == 0)) for i in range(100)]
        assert check_judge_distribution(records).status == CheckStatus.PASS

    def test_near_zero_warns(self):
        records = [make_record(correct_by_judge=(i == 0)) for i in range(200)]
        result = check_judge_distribution(records, warn_if_accuracy_below=0.01)
        assert result.status == CheckStatus.WARN


class TestCheckNoDuplicateResponses:
    def test_all_unique_pass(self):
        records = [
            make_record(response=f"Unique response number {i} with extra text") for i in range(100)
        ]
        assert check_no_duplicate_responses(records).status == CheckStatus.PASS

    def test_many_duplicates_fail(self):
        # 50 identical responses out of 100 → duplicate fraction = 0.5 > 0.1
        records = [
            make_record(response="The exact same stuck response text")
            if i % 2 == 0
            else make_record(response=f"Unique {i}")
            for i in range(100)
        ]
        result = check_no_duplicate_responses(records, max_duplicate_fraction=0.1)
        assert result.status == CheckStatus.FAIL


class TestCheckManifest:
    def test_manifest_json_present_pass(self, tmp_path):
        (tmp_path / "manifest.json").write_text(
            json.dumps({"judge_model": "gpt-4", "split_sha256": "abc", "execution_seed": 42})
        )
        assert check_manifest_present(tmp_path).status == CheckStatus.PASS

    def test_experiment_meta_json_accepted(self, tmp_path):
        (tmp_path / "experiment_meta.json").write_text(json.dumps({"judge_model": "gpt-4"}))
        assert check_manifest_present(tmp_path).status == CheckStatus.PASS

    def test_no_manifest_warns(self, tmp_path):
        """Missing manifest → WARN (provenance gap) not hard FAIL."""
        assert check_manifest_present(tmp_path).status == CheckStatus.WARN

    def test_all_required_fields_pass(self):
        m = {"judge_model": "gpt-4", "split_sha256": "abc123", "execution_seed": 42}
        result = check_manifest_fields(
            m, required=["judge_model", "split_sha256", "execution_seed"]
        )
        assert result.status == CheckStatus.PASS

    def test_missing_required_fields_fail(self):
        m = {"judge_model": "gpt-4"}  # missing split_sha256 and execution_seed
        result = check_manifest_fields(
            m, required=["judge_model", "split_sha256", "execution_seed"]
        )
        assert result.status == CheckStatus.FAIL
        assert "split_sha256" in result.evidence.get("missing", [])
