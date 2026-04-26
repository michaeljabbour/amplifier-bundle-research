"""
test_domain.py — TDD tests for domain.py (RED phase first)

Tests per-category sensitivity analysis: help rates, stratified McNemar,
singleton handling.
"""
from __future__ import annotations


def _make_results(item_ids: list[str], baseline_correct: list[bool],
                  treatment_correct: list[bool],
                  baseline_approach: str = "A0",
                  treatment_approach: str = "A12") -> list[dict]:
    """Build a flat list of results (one record per item×approach)."""
    records = []
    for iid, bc, tc in zip(item_ids, baseline_correct, treatment_correct):
        records.append({"item_id": iid, "approach_id": baseline_approach, "correct_by_judge": bc})
        records.append({"item_id": iid, "approach_id": treatment_approach, "correct_by_judge": tc})
    return records


def _make_items(item_ids: list[str], categories: list[str]) -> list[dict]:
    return [{"item_id": iid, "category": cat} for iid, cat in zip(item_ids, categories)]


# ──────────────────────────────────────────────────────────────────────────────
# Test 1: per-category help rate is computed correctly
# ──────────────────────────────────────────────────────────────────────────────


def test_domain_per_category_help_rate():
    """Help rate for Math category = 6/10 when 6 items flip baseline→wrong to treatment→correct."""
    from amplifier_research_block_hypothesis.domain import compute_domain_sensitivity

    # 10 Math items: baseline correct for 0,1 only; treatment correct for 0-7
    # → n_01 = 6 (items 2-7: baseline wrong, treatment correct)
    # → n_10 = 0 (no items wrong in treatment but right in baseline)
    n = 10
    item_ids = [f"math_{i}" for i in range(n)]
    baseline_correct = [i < 2 for i in range(n)]    # items 0,1 correct
    treatment_correct = [i < 8 for i in range(n)]   # items 0-7 correct

    results = _make_results(item_ids, baseline_correct, treatment_correct)
    items = _make_items(item_ids, ["Math"] * n)

    sensitivity = compute_domain_sensitivity(results, items, "A0", "A12")

    assert "Math" in sensitivity
    math = sensitivity["Math"]
    assert math["n"] == n
    assert math["help_count"] == 6   # n_01
    assert math["hurt_count"] == 0   # n_10
    assert abs(math["help_rate"] - 0.6) < 1e-9


# ──────────────────────────────────────────────────────────────────────────────
# Test 2: stratified McNemar with BH-FDR — significant category shows low q
# ──────────────────────────────────────────────────────────────────────────────


def test_domain_stratified_mcnemar():
    """Math category with n_01=8 is significant after BH-FDR; History is not."""
    from amplifier_research_block_hypothesis.domain import compute_domain_sensitivity

    # Math: n_01=8, n_10=0 (only items 0,1 correct in baseline; ALL correct in treatment)
    # p = 2*(0.5)^8 = 0.0078; BH q (m=2) = 0.0078*2 = 0.0156 < 0.05 ✓
    math_ids = [f"math_{i}" for i in range(10)]
    math_baseline = [i < 2 for i in range(10)]          # items 0,1 correct
    math_treatment = [True] * 10                         # all correct → n_01=8

    # History: n_01=2, n_10=2 → balanced discordant pairs → NOT significant
    # p ≈ 1.0 → BH q = 1.0 > 0.05 ✓
    hist_ids = [f"hist_{i}" for i in range(10)]
    hist_baseline = [True, True, False, False, False, False, False, False, False, False]
    hist_treatment = [False, False, False, False, False, True, True, False, False, False]

    all_ids = math_ids + hist_ids
    all_baseline = math_baseline + hist_baseline
    all_treatment = math_treatment + hist_treatment
    all_categories = ["Math"] * 10 + ["History"] * 10

    results = _make_results(all_ids, all_baseline, all_treatment)
    items = _make_items(all_ids, all_categories)

    sensitivity = compute_domain_sensitivity(results, items, "A0", "A12")

    math = sensitivity["Math"]
    history = sensitivity["History"]

    # Math: n_01=8, n_disc=8 → p=0.0078 → BH q=0.0156 < 0.05
    assert math["bh_q"] < 0.05, f"Math bh_q={math['bh_q']:.4f} should be < 0.05"
    # History: n_01=2, n_10=2 → p≈1.0 → BH q > 0.05
    assert history["bh_q"] > 0.05, f"History bh_q={history['bh_q']:.4f} should be > 0.05"


# ──────────────────────────────────────────────────────────────────────────────
# Test 3: singleton categories are dropped/flagged
# ──────────────────────────────────────────────────────────────────────────────


def test_domain_handles_singleton_categories():
    """Category with n=1 item is either dropped or flagged with dropped=True."""
    from amplifier_research_block_hypothesis.domain import compute_domain_sensitivity

    item_ids = ["item_math_0", "item_math_1", "item_rare_0"]
    categories = ["Math", "Math", "RareCategory"]
    baseline_correct = [True, False, True]
    treatment_correct = [True, True, False]

    results = _make_results(item_ids, baseline_correct, treatment_correct)
    items = _make_items(item_ids, categories)

    sensitivity = compute_domain_sensitivity(results, items, "A0", "A12")

    # RareCategory should be present but flagged
    assert "RareCategory" in sensitivity
    rare = sensitivity["RareCategory"]
    assert rare.get("dropped") is True or rare.get("n", 0) < 2


# ──────────────────────────────────────────────────────────────────────────────
# Bonus: categories with no discordant pairs get p=1.0
# ──────────────────────────────────────────────────────────────────────────────


def test_domain_no_discordant_pairs():
    """When n_01=0 and n_10=0 for a category, McNemar p=1.0 (no detectable effect)."""
    from amplifier_research_block_hypothesis.domain import compute_domain_sensitivity

    item_ids = [f"item_{i}" for i in range(5)]
    # All items agree: baseline and treatment give same result
    baseline_correct = [True, True, False, False, True]
    treatment_correct = [True, True, False, False, True]  # identical

    results = _make_results(item_ids, baseline_correct, treatment_correct)
    items = _make_items(item_ids, ["Physics"] * 5)

    sensitivity = compute_domain_sensitivity(results, items, "A0", "A12")

    assert "Physics" in sensitivity
    phys = sensitivity["Physics"]
    if not phys.get("dropped"):
        assert phys["mcnemar_p"] == 1.0
