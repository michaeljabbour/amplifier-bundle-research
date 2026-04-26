"""
categorize.py — Categorize stage-trace records by empty-failure mode.

Public API:
    categorize_empty(records: list[dict]) -> dict
"""

from __future__ import annotations

# Threshold for what counts as a "substantive" generator/critic output (chars).
_SUBSTANTIVE_THRESHOLD = 100

# All known failure categories.
CATEGORIES = [
    "gen_substantive_critic_empty",
    "gen_substantive_critic_substantive",
    "gen_empty_critic_substantive",
    "gen_empty_critic_empty",
    "gen_substantive_no_critic",
    "unknown",
]


def _is_substantive(stage: dict | None) -> bool:
    """Return True if *stage* has ≥100 chars of output (non-empty)."""
    if stage is None:
        return False
    return (stage.get("output_length", 0) >= _SUBSTANTIVE_THRESHOLD) and (
        not stage.get("is_empty", True)
    )


def _is_empty_stage(stage: dict | None) -> bool:
    """Return True if *stage* is considered empty (zero-length or is_empty flag)."""
    if stage is None:
        return True
    return stage.get("is_empty", False) or stage.get("output_length", 0) == 0


def _classify_record(record: dict) -> str:
    """Return the category name for a single empty-final record."""
    stages = record.get("stages", {})
    generator = stages.get("generator")
    critic = stages.get("critic")  # may be None for A0-style records

    gen_sub = _is_substantive(generator)
    gen_empty = _is_empty_stage(generator)

    if critic is None:
        # A0-style: no critic stage
        if gen_sub:
            return "gen_substantive_no_critic"
        else:
            # gen empty, no critic → fallback to unknown (anomaly)
            return "unknown"

    # critic exists
    crit_sub = _is_substantive(critic)
    crit_empty = _is_empty_stage(critic)

    if gen_sub and crit_empty:
        return "gen_substantive_critic_empty"

    if gen_sub and crit_sub:
        return "gen_substantive_critic_substantive"

    if gen_empty and crit_sub:
        return "gen_empty_critic_substantive"

    if gen_empty and crit_empty:
        return "gen_empty_critic_empty"

    # Fallback: schema gaps or unusual combinations
    return "unknown"


def categorize_empty(records: list[dict]) -> dict:
    """Categorize empty-response failure modes by stage origin.

    Only records where ``final_is_empty == True`` are classified.
    Records where the final response is non-empty are silently ignored.

    Args:
        records: List of stage-trace records (as returned by
            :func:`~amplifier_research_stage_analyzer.ingest.ingest_stage_traces`).

    Returns:
        A dict with two keys:

        - ``"counts"``: ``dict[str, int]`` — count per category.
        - ``"records"``: ``dict[str, list[dict]]`` — raw records per category.

        Categories:

        - ``gen_substantive_critic_empty`` — H1b evidence
        - ``gen_substantive_critic_substantive`` — H1a evidence
        - ``gen_empty_critic_substantive`` — revert preserved generator empty
        - ``gen_empty_critic_empty`` — both stages failed
        - ``gen_substantive_no_critic`` — A0 anomaly
        - ``unknown`` — schema gaps

    Example:
        >>> result = categorize_empty(records)
        >>> result["counts"]["gen_substantive_critic_empty"]
        12
    """
    counts: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    bucketed: dict[str, list[dict]] = {cat: [] for cat in CATEGORIES}

    for record in records:
        if not record.get("final_is_empty", False):
            continue  # only process empty-final records

        category = _classify_record(record)
        counts[category] += 1
        bucketed[category].append(record)

    return {"counts": counts, "records": bucketed}
