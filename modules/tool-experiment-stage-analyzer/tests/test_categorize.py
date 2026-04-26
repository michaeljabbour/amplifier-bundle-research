"""
TDD RED phase — test_categorize.py

Tests for categorize.py: categorize empty-failure modes by stage origin.
All tests MUST FAIL before implementation exists.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _gen(output_length: int = 200, is_empty: bool = False) -> dict:
    return {
        "output": "x" * output_length,
        "output_length": output_length,
        "latency_ms": 1000.0,
        "cost_usd": 0.001,
        "is_empty": is_empty,
        "is_truncated": False,
    }


def _critic(output_length: int = 150, is_empty: bool = False, verdict: str = "keep") -> dict:
    return {
        "output": "y" * output_length,
        "output_length": output_length,
        "latency_ms": 800.0,
        "cost_usd": 0.0008,
        "is_empty": is_empty,
        "verdict": verdict,
    }


def _revert(selected_stage: str = "generator", reason: str = "gen_better") -> dict:
    return {
        "selected_stage": selected_stage,
        "selected_response": "selected text",
        "reason": reason,
    }


def _record(
    item_id: str = "item_001",
    approach_id: str = "A1",
    generator: dict | None = None,
    critic: dict | None = None,
    revert_decision: dict | None = None,
    final_is_empty: bool = True,
    final_response_length: int = 0,
) -> dict:
    return {
        "item_id": item_id,
        "approach_id": approach_id,
        "approach_name": "Reflection",
        "stages": {
            "generator": generator if generator is not None else _gen(),
            "critic": critic,
            "revert_decision": revert_decision,
        },
        "final_response_length": final_response_length,
        "final_is_empty": final_is_empty,
        "timestamp": "2024-01-01T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_categorize_gen_substantive_critic_empty() -> None:
    """Generator is substantive (200 chars), critic is empty, final is empty.

    Expected category: gen_substantive_critic_empty  (H1b evidence).
    """
    from amplifier_research_stage_analyzer.categorize import categorize_empty

    record = _record(
        item_id="item_001",
        generator=_gen(output_length=200, is_empty=False),
        critic=_critic(output_length=0, is_empty=True),
        revert_decision=_revert(reason="both_empty"),
        final_is_empty=True,
        final_response_length=0,
    )
    result = categorize_empty([record])

    assert result["counts"]["gen_substantive_critic_empty"] == 1, (
        f"Expected 1 in gen_substantive_critic_empty, got {result['counts']}"
    )
    assert len(result["records"]["gen_substantive_critic_empty"]) == 1


def test_categorize_both_substantive_revert_empty() -> None:
    """Both generator (200 chars) and critic (200 chars) substantive, final still empty.

    Expected category: gen_substantive_critic_substantive  (H1a evidence).
    """
    from amplifier_research_stage_analyzer.categorize import categorize_empty

    record = _record(
        item_id="item_002",
        generator=_gen(output_length=200, is_empty=False),
        critic=_critic(output_length=200, is_empty=False, verdict="revise"),
        revert_decision=_revert(reason="critic_revise"),
        final_is_empty=True,
        final_response_length=0,
    )
    result = categorize_empty([record])

    assert result["counts"]["gen_substantive_critic_substantive"] == 1, (
        f"Expected 1 in gen_substantive_critic_substantive, got {result['counts']}"
    )
    assert len(result["records"]["gen_substantive_critic_substantive"]) == 1


def test_categorize_both_empty() -> None:
    """Both generator and critic are empty, final is empty.

    Expected category: gen_empty_critic_empty.
    """
    from amplifier_research_stage_analyzer.categorize import categorize_empty

    record = _record(
        item_id="item_003",
        generator=_gen(output_length=0, is_empty=True),
        critic=_critic(output_length=0, is_empty=True, verdict="abstain"),
        revert_decision=_revert(reason="both_empty"),
        final_is_empty=True,
        final_response_length=0,
    )
    result = categorize_empty([record])

    assert result["counts"]["gen_empty_critic_empty"] == 1, (
        f"Expected 1 in gen_empty_critic_empty, got {result['counts']}"
    )
    assert len(result["records"]["gen_empty_critic_empty"]) == 1


def test_categorize_handles_no_critic_records() -> None:
    """A0-style records (critic=null) where generator is non-empty but final_is_empty.

    Expected category: gen_substantive_no_critic  (anomaly).
    """
    from amplifier_research_stage_analyzer.categorize import categorize_empty

    record = _record(
        item_id="item_004",
        approach_id="A0",
        generator=_gen(output_length=200, is_empty=False),
        critic=None,
        revert_decision=None,
        final_is_empty=True,
        final_response_length=0,
    )
    result = categorize_empty([record])

    assert result["counts"]["gen_substantive_no_critic"] == 1, (
        f"Expected 1 in gen_substantive_no_critic, got {result['counts']}"
    )
    assert len(result["records"]["gen_substantive_no_critic"]) == 1


def test_categorize_returns_counts_and_records() -> None:
    """Mixed fixture: verify both counts dict and per-category record lists are returned."""
    from amplifier_research_stage_analyzer.categorize import categorize_empty

    records = [
        # gen_substantive_critic_empty
        _record(
            item_id="mix_001",
            generator=_gen(output_length=200, is_empty=False),
            critic=_critic(output_length=0, is_empty=True),
            revert_decision=_revert(reason="both_empty"),
            final_is_empty=True,
        ),
        # gen_empty_critic_empty
        _record(
            item_id="mix_002",
            generator=_gen(output_length=0, is_empty=True),
            critic=_critic(output_length=0, is_empty=True),
            revert_decision=_revert(reason="both_empty"),
            final_is_empty=True,
        ),
        # gen_substantive_critic_substantive
        _record(
            item_id="mix_003",
            generator=_gen(output_length=200, is_empty=False),
            critic=_critic(output_length=150, is_empty=False, verdict="revise"),
            revert_decision=_revert(reason="critic_revise"),
            final_is_empty=True,
        ),
        # NOT an empty record — should NOT appear in any category
        _record(
            item_id="mix_004",
            generator=_gen(output_length=200, is_empty=False),
            critic=_critic(output_length=150, is_empty=False),
            revert_decision=_revert(),
            final_is_empty=False,
            final_response_length=200,
        ),
    ]

    result = categorize_empty(records)

    # Verify structure
    assert "counts" in result, "Result must have 'counts' key"
    assert "records" in result, "Result must have 'records' key"

    # Only 3 records should be categorized (mix_004 is not empty)
    total_categorized = sum(result["counts"].values())
    assert total_categorized == 3, f"Expected 3 total categorized, got {total_categorized}"

    # Verify counts
    assert result["counts"]["gen_substantive_critic_empty"] == 1
    assert result["counts"]["gen_empty_critic_empty"] == 1
    assert result["counts"]["gen_substantive_critic_substantive"] == 1

    # Verify record IDs in each bucket
    ids_gen_sub_crit_empty = [r["item_id"] for r in result["records"]["gen_substantive_critic_empty"]]
    assert "mix_001" in ids_gen_sub_crit_empty

    ids_gen_empty_crit_empty = [r["item_id"] for r in result["records"]["gen_empty_critic_empty"]]
    assert "mix_002" in ids_gen_empty_crit_empty

    ids_both_sub = [r["item_id"] for r in result["records"]["gen_substantive_critic_substantive"]]
    assert "mix_003" in ids_both_sub
