"""
TDD RED phase — test_analyze.py

Tests for analyze.py: hypothesis test and aggregation logic.
All tests MUST FAIL before implementation exists.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Fixture helpers — build categorize_result dicts directly
# ---------------------------------------------------------------------------

_ALL_CATEGORIES = [
    "gen_substantive_critic_empty",
    "gen_substantive_critic_substantive",
    "gen_empty_critic_substantive",
    "gen_empty_critic_empty",
    "gen_substantive_no_critic",
    "unknown",
]


def _make_categorize_result(
    gen_sub_crit_empty: int = 0,
    gen_sub_crit_sub: int = 0,
    gen_empty_crit_sub: int = 0,
    gen_empty_crit_empty: int = 0,
    gen_sub_no_critic: int = 0,
    unknown: int = 0,
) -> dict:
    """Build a synthetic categorize_result with specified counts."""
    counts = {
        "gen_substantive_critic_empty": gen_sub_crit_empty,
        "gen_substantive_critic_substantive": gen_sub_crit_sub,
        "gen_empty_critic_substantive": gen_empty_crit_sub,
        "gen_empty_critic_empty": gen_empty_crit_empty,
        "gen_substantive_no_critic": gen_sub_no_critic,
        "unknown": unknown,
    }
    # Build minimal record stubs so evidence list can contain item_ids
    records: dict = {cat: [] for cat in _ALL_CATEGORIES}

    def _stub(item_id: str) -> dict:
        return {"item_id": item_id}

    idx = 0
    for _ in range(gen_sub_crit_empty):
        records["gen_substantive_critic_empty"].append(_stub(f"gsce_{idx}"))
        idx += 1
    for _ in range(gen_sub_crit_sub):
        records["gen_substantive_critic_substantive"].append(_stub(f"gscs_{idx}"))
        idx += 1
    for _ in range(gen_empty_crit_sub):
        records["gen_empty_critic_substantive"].append(_stub(f"gecs_{idx}"))
        idx += 1
    for _ in range(gen_empty_crit_empty):
        records["gen_empty_critic_empty"].append(_stub(f"gece_{idx}"))
        idx += 1
    for _ in range(gen_sub_no_critic):
        records["gen_substantive_no_critic"].append(_stub(f"gsnc_{idx}"))
        idx += 1
    for _ in range(unknown):
        records["unknown"].append(_stub(f"unk_{idx}"))
        idx += 1

    return {"counts": counts, "records": records}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_h1a_confirmation_threshold() -> None:
    """H1a is confirmed when (gen_sub_crit_sub + gen_sub_crit_empty) / total >= 0.40.

    Fixture: 4 gen_substantive_critic_empty + 4 gen_substantive_critic_substantive
             out of 10 total empties → fraction = 8/10 = 0.80 >= 0.40 → h1a_confirmed=True.
    """
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses

    cat_result = _make_categorize_result(
        gen_sub_crit_empty=4,
        gen_sub_crit_sub=4,
        gen_empty_crit_empty=2,
    )
    result = test_h1_hypotheses(cat_result)

    assert "h1a_confirmed" in result
    assert "h1a_fraction" in result
    assert result["h1a_confirmed"] is True, (
        f"Expected h1a_confirmed=True, fraction={result.get('h1a_fraction')}"
    )
    assert abs(result["h1a_fraction"] - 0.80) < 1e-9, (
        f"Expected h1a_fraction=0.80, got {result['h1a_fraction']}"
    )


def test_h1b_confirmation_threshold() -> None:
    """H1b is confirmed when gen_sub_crit_empty / total >= 0.40.

    Fixture: 5 gen_substantive_critic_empty out of 10 total → fraction = 0.50 >= 0.40 → confirmed.
    """
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses

    cat_result = _make_categorize_result(
        gen_sub_crit_empty=5,
        gen_empty_crit_empty=5,
    )
    result = test_h1_hypotheses(cat_result)

    assert result["h1b_confirmed"] is True, (
        f"Expected h1b_confirmed=True, fraction={result.get('h1b_fraction')}"
    )
    assert abs(result["h1b_fraction"] - 0.50) < 1e-9, (
        f"Expected h1b_fraction=0.50, got {result['h1b_fraction']}"
    )


def test_h1a_h1b_both_below_threshold() -> None:
    """When most empties come from gen_empty (not gen_substantive), neither H1a nor H1b confirms.

    Fixture: 2 gen_sub_crit_empty + 0 gen_sub_crit_sub out of 10 → h1a=0.20, h1b=0.20, both False.
    """
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses

    cat_result = _make_categorize_result(
        gen_sub_crit_empty=2,
        gen_empty_crit_empty=8,
    )
    result = test_h1_hypotheses(cat_result)

    assert result["h1a_confirmed"] is False, (
        f"Expected h1a_confirmed=False, got {result['h1a_confirmed']}"
    )
    assert result["h1b_confirmed"] is False, (
        f"Expected h1b_confirmed=False, got {result['h1b_confirmed']}"
    )
    assert result["h1a_fraction"] < 0.40
    assert result["h1b_fraction"] < 0.40


def test_evidence_records_returned() -> None:
    """Confirmation results include 'evidence' list with item_ids of supporting records."""
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses

    cat_result = _make_categorize_result(
        gen_sub_crit_empty=5,
        gen_sub_crit_sub=3,
        gen_empty_crit_empty=2,
    )
    result = test_h1_hypotheses(cat_result)

    assert "evidence" in result, "Expected 'evidence' key in hypothesis test result"
    evidence = result["evidence"]
    assert isinstance(evidence, list), f"Expected evidence to be a list, got {type(evidence)}"
    # Evidence should contain item_ids from confirming categories
    # With 5 gen_sub_crit_empty + 3 gen_sub_crit_sub out of 10 → h1a_confirmed=True
    assert len(evidence) > 0, "Expected non-empty evidence list when hypothesis confirmed"
    # Each evidence item should have an item_id
    for ev in evidence:
        assert "item_id" in ev, f"Evidence item missing 'item_id': {ev}"


def test_hypothesis_test_zero_empties() -> None:
    """When there are no empty records at all, fractions are 0.0 and neither is confirmed."""
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses

    cat_result = _make_categorize_result()  # all zeros
    result = test_h1_hypotheses(cat_result)

    assert result["h1a_confirmed"] is False
    assert result["h1b_confirmed"] is False
    assert result["h1a_fraction"] == 0.0
    assert result["h1b_fraction"] == 0.0
