"""
test_ablation.py — TDD tests for ablation.py (RED phase first)

Tests multi-condition ablation comparison: paired deltas, block value added,
empty rates, and markdown table format.
"""
from __future__ import annotations

import json
import os
import tempfile


def _write_results(path: str, records: list[dict]) -> None:
    """Write a list of result dicts as a .jsonl file."""
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


def _make_result(item_id: str, correct: bool, is_empty: bool = False) -> dict:
    return {"item_id": item_id, "correct_by_judge": correct, "is_empty": is_empty}


# ──────────────────────────────────────────────────────────────────────────────
# Test 1: paired delta computed for each condition vs C0
# ──────────────────────────────────────────────────────────────────────────────


def test_ablation_paired_delta_per_condition():
    """4 conditions × 100 items → 4 paired deltas computed."""
    from amplifier_research_block_hypothesis.ablation import compute_ablation_summary

    n = 100
    item_ids = [f"item_{i}" for i in range(n)]

    # C0: correct for items 0–39 (40% accuracy)
    c0 = [_make_result(iid, i < 40) for i, iid in enumerate(item_ids)]

    # Condition A: 10 more correct than C0 (items 40-49 flip to correct)
    cond_a = [_make_result(iid, i < 50) for i, iid in enumerate(item_ids)]
    # Condition B: 5 less correct than C0
    cond_b = [_make_result(iid, i < 35) for i, iid in enumerate(item_ids)]
    # Condition C: same as C0
    cond_c = [_make_result(iid, i < 40) for i, iid in enumerate(item_ids)]
    # Condition D: 20 more correct
    cond_d = [_make_result(iid, i < 60) for i, iid in enumerate(item_ids)]

    conditions_results = {
        "C0": c0,
        "C3_alone": cond_a,
        "C3_block_only": cond_b,
        "C3_appendix_only": cond_c,
        "C3_both": cond_d,
    }

    summary = compute_ablation_summary(conditions_results, baseline="C0")

    # 4 non-baseline conditions
    assert len(summary["deltas"]) == 4
    for cond in ["C3_alone", "C3_block_only", "C3_appendix_only", "C3_both"]:
        assert cond in summary["deltas"]
        assert "delta" in summary["deltas"][cond]
        assert "mcnemar_p" in summary["deltas"][cond]


# ──────────────────────────────────────────────────────────────────────────────
# Test 2: block value added (C3_block_only vs C3_alone delta)
# ──────────────────────────────────────────────────────────────────────────────


def test_ablation_block_value_added():
    """C3_block_only vs C3_alone comparison reports an explicit block_value_added delta."""
    from amplifier_research_block_hypothesis.ablation import compute_ablation_summary

    n = 100
    item_ids = [f"item_{i}" for i in range(n)]

    c0 = [_make_result(iid, i < 40) for i, iid in enumerate(item_ids)]
    # C3_alone: 50% accuracy
    c3_alone = [_make_result(iid, i < 50) for i, iid in enumerate(item_ids)]
    # C3_block_only: 55% accuracy (block adds 5pp over C3_alone)
    c3_block = [_make_result(iid, i < 55) for i, iid in enumerate(item_ids)]

    conditions_results = {
        "C0": c0,
        "C3_alone": c3_alone,
        "C3_block_only": c3_block,
    }

    summary = compute_ablation_summary(conditions_results, baseline="C0")

    assert "block_value_added" in summary
    bva = summary["block_value_added"]
    assert bva is not None
    # C3_block_only has 5 more correct than C3_alone → positive delta
    assert bva["delta"] > 0
    assert "n_01" in bva  # items where C3_alone wrong, C3_block correct
    assert "n_10" in bva  # items where C3_alone correct, C3_block wrong


# ──────────────────────────────────────────────────────────────────────────────
# Test 3: empty rate per condition
# ──────────────────────────────────────────────────────────────────────────────


def test_ablation_empty_rate_per_condition():
    """Empty rate reflects actual fraction of empty responses per condition."""
    from amplifier_research_block_hypothesis.ablation import compute_ablation_summary

    n = 20
    item_ids = [f"item_{i}" for i in range(n)]

    c0 = [_make_result(iid, True, is_empty=False) for iid in item_ids]
    # Treatment: 4 out of 20 are empty (20% empty rate)
    treatment = [
        _make_result(iid, i >= 4, is_empty=(i < 4)) for i, iid in enumerate(item_ids)
    ]

    conditions_results = {"C0": c0, "C3_block": treatment}
    summary = compute_ablation_summary(conditions_results, baseline="C0")

    assert "C3_block" in summary["deltas"]
    empty_rate = summary["deltas"]["C3_block"]["empty_rate"]
    assert abs(empty_rate - 0.20) < 1e-9  # exactly 4/20 = 0.20


# ──────────────────────────────────────────────────────────────────────────────
# Test 4: markdown summary table contains expected column headers
# ──────────────────────────────────────────────────────────────────────────────


def test_ablation_summary_table_format():
    """Markdown output contains a table with required column headers."""
    from amplifier_research_block_hypothesis.ablation import (
        ablation_to_markdown,
        compute_ablation_summary,
    )

    n = 50
    item_ids = [f"item_{i}" for i in range(n)]
    c0 = [_make_result(iid, i < 25) for i, iid in enumerate(item_ids)]
    cond = [_make_result(iid, i < 30) for i, iid in enumerate(item_ids)]

    summary = compute_ablation_summary({"C0": c0, "C3_block": cond}, baseline="C0")
    md = ablation_to_markdown(summary)

    # Must contain a Markdown table with expected headers
    assert "| Condition" in md or "|Condition" in md
    assert "delta" in md.lower() or "Δ" in md
    assert "p-value" in md.lower() or "p_value" in md.lower() or "mcnemar" in md.lower()
    assert "empty" in md.lower()
