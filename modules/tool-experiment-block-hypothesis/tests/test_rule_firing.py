"""
test_rule_firing.py — TDD tests for rule_firing.py (RED phase first)

Tests per-rule firing heuristics: keyword match, no-match, multi-record
aggregation, and per-rule-dict structure.
"""
from __future__ import annotations

import pytest


def _make_trace(item_id: str, critic_text: str | None, final_is_empty: bool = False) -> dict:
    """Helper: build a minimal stage-trace dict."""
    return {
        "item_id": item_id,
        "approach_id": "A12a",
        "approach_name": "test",
        "stages": {
            "generator": {
                "output": "answer",
                "output_length": 6,
                "latency_ms": 100.0,
                "cost_usd": 0.001,
                "is_empty": False,
                "is_truncated": False,
            },
            "critic": {"output": critic_text} if critic_text is not None else None,
            "revert_decision": {"reverted": False} if critic_text else None,
        },
        "final_response_length": 0 if final_is_empty else 100,
        "final_is_empty": final_is_empty,
        "timestamp": "2026-01-01T00:00:00+00:00",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Test 1: keyword match causes fires_count = 1
# ──────────────────────────────────────────────────────────────────────────────


def test_rule_firing_keyword_match():
    """Rule with 'arithmetic' keyword fires when critic_output contains 'arithmetic'."""
    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing

    rule = {
        "mechanism": "ARITHMETIC_ERROR",
        "trigger": "always check arithmetic in responses",
        "action": "recheck arithmetic carefully",
        "token": "RT_CHECK_ARITHMETIC",
    }
    block = {"rules": [rule]}
    traces = [_make_trace("item_1", "The arithmetic here is wrong, check arithmetic again")]

    result = analyze_rule_firing(block, traces)

    assert "RT_CHECK_ARITHMETIC" in result
    assert result["RT_CHECK_ARITHMETIC"]["fires_count"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Test 2: no keyword match → fires_count = 0
# ──────────────────────────────────────────────────────────────────────────────


def test_rule_firing_no_match():
    """Rule with spatial/board keywords doesn't fire against unrelated critic text."""
    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing

    rule = {
        "mechanism": "SPATIAL_REASONING_ERROR",
        "trigger": "board position verification required",
        "action": "verify spatial state after every move",
        "token": "RT_VERIFY_SPATIAL_STATE",
    }
    block = {"rules": [rule]}
    traces = [_make_trace("item_1", "The answer looks correct based on historical context")]

    result = analyze_rule_firing(block, traces)

    assert "RT_VERIFY_SPATIAL_STATE" in result
    assert result["RT_VERIFY_SPATIAL_STATE"]["fires_count"] == 0


# ──────────────────────────────────────────────────────────────────────────────
# Test 3: multi-record aggregation — exactly 3 of 5 records fire
# ──────────────────────────────────────────────────────────────────────────────


def test_rule_firing_multi_record_aggregation():
    """3 of 5 traces contain rule keywords → fires_count = 3."""
    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing

    rule = {
        "mechanism": "CONFIDENT_MISRECALL",
        "trigger": "verify factual claims carefully",
        "action": "double check factual accuracy",
        "token": "RT_VERIFY_FACTUAL_CLAIM",
    }
    block = {"rules": [rule]}

    traces = [
        # Fires: "factual" and "claims" both appear
        _make_trace("item_1", "verify the factual claims here before concluding"),
        # No fire: no rule keywords
        _make_trace("item_2", "the answer seems totally correct to me"),
        # Fires: "factual" appears
        _make_trace("item_3", "factual accuracy is questionable in this response"),
        # Fires: "carefully" appears from trigger
        _make_trace("item_4", "I carefully verified the factual content here"),
        # No fire: no rule keywords
        _make_trace("item_5", "nothing special to note about this answer"),
    ]

    result = analyze_rule_firing(block, traces)

    assert result["RT_VERIFY_FACTUAL_CLAIM"]["fires_count"] == 3


# ──────────────────────────────────────────────────────────────────────────────
# Test 4: 7-rule block → dict has 7 keys
# ──────────────────────────────────────────────────────────────────────────────


def test_rule_firing_returns_per_rule_dict():
    """Block with 7 rules → result dict has exactly 7 keys (one per rule)."""
    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing

    rules = [
        {
            "mechanism": f"RULE_{i}",
            "trigger": f"trigger phrase number {i} for testing",
            "action": f"action description number {i}",
            "token": f"RT_RULE_{i}",
        }
        for i in range(7)
    ]
    block = {"rules": rules}
    traces: list[dict] = []  # empty traces — just check structure

    result = analyze_rule_firing(block, traces)

    assert len(result) == 7
    for i in range(7):
        assert f"RT_RULE_{i}" in result


# ──────────────────────────────────────────────────────────────────────────────
# Bonus test: helped/hurt/neutral counts are non-negative and sum to fires_count
# ──────────────────────────────────────────────────────────────────────────────


def test_rule_firing_counts_are_consistent():
    """helped + hurt + neutral == fires_count for each rule."""
    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing

    rule = {
        "mechanism": "CALCULATION_DRIFT",
        "trigger": "multi-step derivation calculation verification",
        "action": "re-derive calculation from original constraints",
        "token": "RT_RECHECK_DERIVATION",
    }
    block = {"rules": [rule]}
    traces = [
        _make_trace("item_1", "the calculation derivation needs re-verification", final_is_empty=False),
        _make_trace("item_2", "re-derive the multi-step calculation here", final_is_empty=True),
        _make_trace("item_3", "unrelated content about history", final_is_empty=False),
    ]

    result = analyze_rule_firing(block, traces)
    stats = result["RT_RECHECK_DERIVATION"]

    total = stats["helped_count"] + stats["hurt_count"] + stats["neutral_count"]
    assert total == stats["fires_count"]
    assert stats["fires_count"] >= 0
