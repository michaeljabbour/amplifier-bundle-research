"""
analyze.py — Aggregate stats and hypothesis tests.

Public API:
    test_h1_hypotheses(categorize_result: dict) -> dict
"""

from __future__ import annotations

# Pre-registered confirmation threshold (reflection-tokens pre-registration §2.3).
_H1_THRESHOLD = 0.40


def test_h1_hypotheses(categorize_result: dict) -> dict:
    """Apply pre-registered H1a and H1b confirmation criteria.

    Per reflection-tokens pre-registration §2.3:

    - **H1a confirmed** if
      ``(gen_substantive_critic_substantive + gen_substantive_critic_empty)
      / total_empties ≥ 0.40``
    - **H1b confirmed** if
      ``gen_substantive_critic_empty / total_empties ≥ 0.40``

    Args:
        categorize_result: The dict returned by
            :func:`~amplifier_research_stage_analyzer.categorize.categorize_empty`.

    Returns:
        Dict with keys:

        - ``h1a_confirmed`` (bool)
        - ``h1a_fraction`` (float)
        - ``h1b_confirmed`` (bool)
        - ``h1b_fraction`` (float)
        - ``evidence`` (list[dict]) — records from confirming categories

    Example:
        >>> result = test_h1_hypotheses(categorize_result)
        >>> result["h1a_confirmed"]
        True
    """
    counts = categorize_result["counts"]
    records = categorize_result["records"]

    total_empties = sum(counts.values())

    gsce = counts.get("gen_substantive_critic_empty", 0)
    gscs = counts.get("gen_substantive_critic_substantive", 0)

    if total_empties == 0:
        h1a_fraction = 0.0
        h1b_fraction = 0.0
    else:
        h1a_fraction = (gscs + gsce) / total_empties
        h1b_fraction = gsce / total_empties

    h1a_confirmed = h1a_fraction >= _H1_THRESHOLD
    h1b_confirmed = h1b_fraction >= _H1_THRESHOLD

    # Build evidence list: records from categories that support H1a (the broader criterion)
    evidence: list[dict] = []
    if h1a_confirmed:
        evidence.extend(records.get("gen_substantive_critic_empty", []))
        evidence.extend(records.get("gen_substantive_critic_substantive", []))
    elif h1b_confirmed:
        evidence.extend(records.get("gen_substantive_critic_empty", []))

    return {
        "h1a_confirmed": h1a_confirmed,
        "h1a_fraction": h1a_fraction,
        "h1b_confirmed": h1b_confirmed,
        "h1b_fraction": h1b_fraction,
        "evidence": evidence,
    }
