"""
ablation.py — Multi-condition ablation comparison for block experiments.

Given per-condition result files (one results.jsonl per condition), computes:
  - Paired Δ vs baseline (C0) for each condition
  - McNemar exact p-value
  - Empty rate per condition
  - Help:hurt ratio per condition
  - Block added value (C3_block_only vs C3_alone, if both present)
"""

from __future__ import annotations

import math
from typing import Optional

try:
    from scipy.stats import binomtest
except ImportError:
    binomtest = None  # type: ignore[assignment]


# ─────────────────────────────────────────────────────────────────────────────
# Statistical helpers
# ─────────────────────────────────────────────────────────────────────────────


def _mcnemar_p(n_01: int, n_10: int) -> float:
    """Exact two-tailed McNemar p-value using binomial test.

    Under H0 (no difference), the probability that a discordant pair favours
    treatment is 0.5.  Returns 1.0 when n_discordant == 0.
    """
    n_disc = n_01 + n_10
    if n_disc == 0:
        return 1.0
    # Two-tailed: p = 2 * min(P(X <= min(n_01, n_10)), P(X >= max(n_01, n_10)))
    if binomtest is not None:
        result = binomtest(max(n_01, n_10), n_disc, 0.5, alternative="greater")
        return float(min(1.0, 2.0 * float(result.pvalue)))
    # Fallback: normal approximation with continuity correction
    z = (abs(n_01 - n_10) - 1.0) / math.sqrt(n_disc)
    # Two-tailed from standard normal CDF approximation
    # Using erfc for simplicity
    p = math.erfc(z / math.sqrt(2))
    return min(1.0, p)


def _compute_pair_stats(
    baseline_results: list[dict],
    treatment_results: list[dict],
) -> dict:
    """Compute paired McNemar stats between two condition result lists.

    Joins on ``item_id``.  Returns a stats dict with delta, n_01, n_10,
    n_paired, mcnemar_p, empty_rate, help_hurt_ratio.
    """
    base_by_id = {r["item_id"]: r for r in baseline_results}
    treat_by_id = {r["item_id"]: r for r in treatment_results}

    common_ids = set(base_by_id) & set(treat_by_id)

    n_01 = 0  # baseline wrong, treatment correct
    n_10 = 0  # baseline correct, treatment wrong
    n_11 = 0  # both correct
    n_00 = 0  # both wrong

    for iid in common_ids:
        b_correct = bool(base_by_id[iid].get("correct_by_judge", False))
        t_correct = bool(treat_by_id[iid].get("correct_by_judge", False))
        if not b_correct and t_correct:
            n_01 += 1
        elif b_correct and not t_correct:
            n_10 += 1
        elif b_correct and t_correct:
            n_11 += 1
        else:
            n_00 += 1

    n_paired = len(common_ids)
    delta = ((n_01 - n_10) / n_paired * 100.0) if n_paired > 0 else 0.0
    p = _mcnemar_p(n_01, n_10)

    # Empty rate is specific to the treatment condition
    n_empty = sum(1 for r in treatment_results if r.get("is_empty", False))
    empty_rate = n_empty / len(treatment_results) if treatment_results else 0.0

    help_hurt_ratio = (n_01 / max(n_10, 1)) if n_01 > 0 else float(n_01)

    return {
        "delta": delta,
        "n_01": n_01,
        "n_10": n_10,
        "n_11": n_11,
        "n_00": n_00,
        "n_paired": n_paired,
        "mcnemar_p": p,
        "empty_rate": empty_rate,
        "help_hurt_ratio": help_hurt_ratio,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def compute_ablation_summary(
    conditions_results: dict[str, list[dict]],
    baseline: str = "C0",
) -> dict:
    """Compute multi-condition ablation summary.

    For each non-baseline condition, computes paired stats vs *baseline*.
    If both ``C3_alone`` and ``C3_block_only`` are present, also reports
    the incremental ``block_value_added`` delta between them.

    Args:
        conditions_results: Mapping of condition name → list of result records.
            Each record must have ``item_id`` and ``correct_by_judge``.
            Optional: ``is_empty`` for empty-rate computation.
        baseline: Name of the baseline condition (default ``"C0"``).

    Returns:
        ``{
            "deltas": {condition: {delta, n_01, n_10, n_paired, mcnemar_p,
                                   empty_rate, help_hurt_ratio}},
            "block_value_added": {...} or None
        }``
    """
    baseline_results = conditions_results.get(baseline, [])
    deltas: dict[str, dict] = {}

    for cond_name, cond_results in conditions_results.items():
        if cond_name == baseline:
            continue
        stats = _compute_pair_stats(baseline_results, cond_results)
        deltas[cond_name] = stats

    # Block added value: C3_block_only minus C3_alone (if both present)
    block_value_added: Optional[dict] = None
    if "C3_alone" in conditions_results and "C3_block_only" in conditions_results:
        block_value_added = _compute_pair_stats(
            conditions_results["C3_alone"],
            conditions_results["C3_block_only"],
        )

    return {
        "deltas": deltas,
        "block_value_added": block_value_added,
        "baseline": baseline,
    }


def ablation_to_markdown(summary: dict, output_path: str | None = None) -> str:
    """Render ablation summary as a Markdown comparison table.

    Args:
        summary: Output of :func:`compute_ablation_summary`.
        output_path: Optional path to write the report.

    Returns:
        Markdown-formatted report string.
    """
    baseline = summary.get("baseline", "C0")
    deltas = summary.get("deltas", {})

    lines: list[str] = [
        "# Ablation Summary",
        "",
        f"Baseline condition: **{baseline}**",
        "",
        "## Condition Comparison Table",
        "",
        "| Condition | Δ vs C0 (pp) | McNemar p | Empty Rate | Help:Hurt | n_01 | n_10 |",
        "| --------- | -----------: | ---------:| ----------:| ---------:| ----:| ----:|",
    ]

    for cond, stats in deltas.items():
        delta_str = f"{stats['delta']:+.2f}"
        p_str = f"{stats['mcnemar_p']:.4f}"
        empty_str = f"{stats['empty_rate']:.3f}"
        hh_str = f"{stats['help_hurt_ratio']:.2f}"
        lines.append(
            f"| {cond} | {delta_str} | {p_str} | {empty_str} | {hh_str} "
            f"| {stats['n_01']} | {stats['n_10']} |"
        )

    lines += [""]

    # Block added value section
    bva = summary.get("block_value_added")
    if bva is not None:
        lines += [
            "## Block Value Added (C3_block_only vs C3_alone)",
            "",
            f"- Δ: **{bva['delta']:+.2f} pp**",
            f"- n_01 (block helps): {bva['n_01']}",
            f"- n_10 (block hurts): {bva['n_10']}",
            f"- McNemar p: {bva['mcnemar_p']:.4f}",
            f"- Help:Hurt ratio: {bva['help_hurt_ratio']:.2f}",
            "",
            (
                "**Interpretation:** The block adds value beyond C3 alone "
                f"({'positive Δ' if bva['delta'] > 0 else 'no positive Δ'}; "
                f"p={bva['mcnemar_p']:.4f})."
            ),
            "",
        ]

    report = "\n".join(lines)

    if output_path:
        from pathlib import Path

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")

    return report
