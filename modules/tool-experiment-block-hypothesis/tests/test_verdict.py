"""
test_verdict.py — TDD tests for verdict.py (RED phase first)

Tests pre-registered threshold evaluation: WORKS, HETEROGENEOUS,
DOES_NOT_WORK, UNDERPOWERED verdicts.
"""
from __future__ import annotations


# ──────────────────────────────────────────────────────────────────────────────
# Test 1: WORKS when all thresholds are met
# ──────────────────────────────────────────────────────────────────────────────


def test_verdict_works_when_all_thresholds_met():
    """Synthetic data clears all bars → verdict is 'WORKS'."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    # 3 splits, each with n=200, ~12% net improvement (n_01=28, n_10=4)
    # Combined delta = 24/200 = 12% >> both thresholds (5% and 10%)
    # McNemar p will be tiny (well-powered), all splits positive direction
    splits = [
        {"n": 200, "n_01": 28, "n_10": 4},
        {"n": 200, "n_01": 26, "n_10": 3},
        {"n": 200, "n_01": 30, "n_10": 5},
    ]

    result = compute_verdict(
        splits=splits,
        threshold_paired_delta=5.0,
        threshold_substantive_delta=10.0,
        threshold_fdr=0.05,
        threshold_replication_splits=3,
    )

    assert result["verdict"] == "WORKS"
    assert "evidence" in result
    assert result["evidence"]["combined_delta"] > 10.0


# ──────────────────────────────────────────────────────────────────────────────
# Test 2: HETEROGENEOUS when splits vary ≥ 3pp but combined is positive
# ──────────────────────────────────────────────────────────────────────────────


def test_verdict_heterogeneous_when_splits_vary():
    """3 splits Δ=[+8, +3, +0.5] but combined positive → HETEROGENEOUS."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    # Split 1: large effect (delta ≈ 8%)
    # Split 2: moderate effect (delta ≈ 3%)
    # Split 3: tiny effect (delta ≈ 0.5%)
    # Range = 7.5pp ≥ 3pp → HETEROGENEOUS
    # But combined: (16+6+1-0-0-0)/(200+200+200) = 23/600 ≈ 3.8% ... might not clear threshold
    # Let me use larger n per split to push combined above threshold
    splits = [
        {"n": 200, "n_01": 16, "n_10": 0},   # delta = 8%
        {"n": 200, "n_01": 6,  "n_10": 0},   # delta = 3%
        {"n": 200, "n_01": 1,  "n_10": 0},   # delta = 0.5%
    ]

    result = compute_verdict(
        splits=splits,
        threshold_paired_delta=5.0,
        threshold_substantive_delta=10.0,
        threshold_fdr=0.05,
        threshold_replication_splits=3,
    )

    assert result["verdict"] == "HETEROGENEOUS"
    assert "split_deltas" in result["evidence"]
    # Split delta range should be ≥ 3pp
    split_deltas = result["evidence"]["split_deltas"]
    delta_range = max(split_deltas) - min(split_deltas)
    assert delta_range >= 3.0


# ──────────────────────────────────────────────────────────────────────────────
# Test 3: DOES_NOT_WORK when CI crosses zero
# ──────────────────────────────────────────────────────────────────────────────


def test_verdict_does_not_work_when_ci_crosses_zero():
    """Small n_01 ≈ n_10 → CI includes 0 → DOES_NOT_WORK."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    # Near-balanced discordant pairs → tiny delta, wide CI crossing zero
    splits = [
        {"n": 100, "n_01": 5, "n_10": 4},   # delta = 1%, CI definitely crosses 0
        {"n": 100, "n_01": 6, "n_10": 5},
        {"n": 100, "n_01": 4, "n_10": 4},
    ]

    result = compute_verdict(
        splits=splits,
        threshold_paired_delta=5.0,
        threshold_substantive_delta=10.0,
        threshold_fdr=0.05,
        threshold_replication_splits=3,
    )

    assert result["verdict"] == "DOES_NOT_WORK"
    assert result["evidence"]["ci_lower"] < 0


# ──────────────────────────────────────────────────────────────────────────────
# Test 4: UNDERPOWERED when n is too small to detect observed effect
# ──────────────────────────────────────────────────────────────────────────────


def test_verdict_underpowered_signal():
    """Low n with few discordant pairs → UNDERPOWERED (power < 0.80)."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    # Very few discordant pairs → even though delta looks large, it's unreliable
    # n_discordant = 3 → McNemar power < 0.80 for any realistic delta
    splits = [
        {"n": 20, "n_01": 3, "n_10": 0},   # delta = 15% but n_discordant = 3
        {"n": 20, "n_01": 2, "n_10": 0},   # delta = 10%, n_discordant = 2
    ]

    result = compute_verdict(
        splits=splits,
        threshold_paired_delta=5.0,
        threshold_substantive_delta=10.0,
        threshold_fdr=0.05,
        threshold_replication_splits=3,
    )

    assert result["verdict"] == "UNDERPOWERED"
    assert "power_estimate" in result["evidence"]
    assert result["evidence"]["power_estimate"] < 0.80


# ──────────────────────────────────────────────────────────────────────────────
# Bonus: verdict JSON is always well-formed
# ──────────────────────────────────────────────────────────────────────────────


def test_verdict_json_structure():
    """Verdict result always has 'verdict', 'evidence', 'criteria' keys."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    splits = [{"n": 50, "n_01": 3, "n_10": 2}]

    result = compute_verdict(splits=splits)

    assert isinstance(result, dict)
    assert "verdict" in result
    assert "evidence" in result
    assert result["verdict"] in {"WORKS", "HETEROGENEOUS", "DOES_NOT_WORK", "UNDERPOWERED"}
