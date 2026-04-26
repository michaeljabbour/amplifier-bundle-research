"""
domain.py — Per-category (domain) sensitivity analysis.

For each category in the items, computes help/hurt rates of treatment vs
baseline, applies per-category McNemar exact tests, then corrects for
multiple comparisons using Benjamini-Hochberg FDR.
"""

from __future__ import annotations

import math
from collections import defaultdict

try:
    from scipy.stats import binomtest
except ImportError:
    binomtest = None  # type: ignore[assignment]


# ─────────────────────────────────────────────────────────────────────────────
# Statistical helpers
# ─────────────────────────────────────────────────────────────────────────────

_MIN_N_FOR_TEST = 2  # Categories with fewer items are flagged as dropped


def _mcnemar_p_exact(n_01: int, n_10: int) -> float:
    """Exact two-tailed McNemar p-value via binomial test."""
    n_disc = n_01 + n_10
    if n_disc == 0:
        return 1.0
    if binomtest is not None:
        result = binomtest(max(n_01, n_10), n_disc, 0.5, alternative="greater")
        return float(min(1.0, 2.0 * float(result.pvalue)))
    # Normal approximation fallback
    z = (abs(n_01 - n_10) - 1.0) / math.sqrt(n_disc)
    p = math.erfc(z / math.sqrt(2))
    return min(1.0, max(0.0, p))


def _bh_fdr_correction(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg FDR correction.

    Returns a list of adjusted q-values (same order as input p_values).
    """
    m = len(p_values)
    if m == 0:
        return []

    # Sort by p-value ascending, tracking original indices
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    q_values = [0.0] * m

    # BH: q_i = p_i * m / rank (where rank is 1-indexed position in sorted order)
    # Apply cumulative minimum from the largest to prevent non-monotonicity
    prev_q = float("inf")
    for rev_rank, (orig_idx, pval) in enumerate(reversed(indexed)):
        rank = m - rev_rank  # rank of this p-value in sorted order (1 = smallest)
        q = pval * m / rank
        q = min(q, prev_q)
        q_values[orig_idx] = min(q, 1.0)
        prev_q = q

    return q_values


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def compute_domain_sensitivity(
    results: list[dict],
    items: list[dict],
    baseline_approach: str,
    treatment_approach: str,
) -> dict[str, dict]:
    """Compute per-category help/hurt rates and stratified McNemar with BH-FDR.

    Args:
        results: Flat list of result records, one per (item_id, approach_id).
            Each record must have ``item_id``, ``approach_id``, and
            ``correct_by_judge``.
        items: List of item metadata records, each with ``item_id`` and
            ``category``.
        baseline_approach: Approach ID for the baseline condition.
        treatment_approach: Approach ID for the treatment condition.

    Returns:
        Mapping of category → per-category stats dict with keys:
        ``n``, ``help_count`` (n_01), ``hurt_count`` (n_10),
        ``tie_correct`` (n_11), ``tie_wrong`` (n_00),
        ``help_rate``, ``mcnemar_p``, ``bh_q``, ``is_significant``, ``dropped``.
    """
    # Index results by (item_id, approach_id)
    result_index: dict[tuple[str, str], bool] = {}
    for rec in results:
        key = (rec["item_id"], rec["approach_id"])
        result_index[key] = bool(rec.get("correct_by_judge", False))

    # Collect per-category discordant counts
    cat_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"n_01": 0, "n_10": 0, "n_11": 0, "n_00": 0, "n": 0}
    )

    for item in items:
        iid = item["item_id"]
        cat = item["category"]
        b_key = (iid, baseline_approach)
        t_key = (iid, treatment_approach)

        if b_key not in result_index or t_key not in result_index:
            continue  # item not in both approaches — skip

        b_correct = result_index[b_key]
        t_correct = result_index[t_key]
        cat_stats[cat]["n"] += 1

        if not b_correct and t_correct:
            cat_stats[cat]["n_01"] += 1
        elif b_correct and not t_correct:
            cat_stats[cat]["n_10"] += 1
        elif b_correct and t_correct:
            cat_stats[cat]["n_11"] += 1
        else:
            cat_stats[cat]["n_00"] += 1

    # Compute McNemar p for each testable category
    categories = list(cat_stats.keys())
    raw_ps: list[float] = []
    dropped_flags: list[bool] = []

    for cat in categories:
        s = cat_stats[cat]
        if s["n"] < _MIN_N_FOR_TEST:
            raw_ps.append(1.0)
            dropped_flags.append(True)
        else:
            p = _mcnemar_p_exact(s["n_01"], s["n_10"])
            raw_ps.append(p)
            dropped_flags.append(False)

    # Apply BH-FDR (only on non-dropped)
    q_values = _bh_fdr_correction(raw_ps)

    # Assemble output
    output: dict[str, dict] = {}
    for i, cat in enumerate(categories):
        s = cat_stats[cat]
        n = s["n"]
        n_01 = s["n_01"]
        n_10 = s["n_10"]
        dropped = dropped_flags[i]
        p = raw_ps[i]
        q = q_values[i]
        help_rate = n_01 / n if n > 0 else 0.0

        output[cat] = {
            "n": n,
            "help_count": n_01,
            "hurt_count": n_10,
            "tie_correct": s["n_11"],
            "tie_wrong": s["n_00"],
            "help_rate": help_rate,
            "mcnemar_p": p,
            "bh_q": q,
            "is_significant": (q < 0.05),
            "dropped": dropped,
        }

    return output


def domain_to_markdown(
    sensitivity: dict[str, dict],
    output_path: str | None = None,
) -> str:
    """Render domain-sensitivity results as a Markdown report.

    Args:
        sensitivity: Output of :func:`compute_domain_sensitivity`.
        output_path: Optional path to write the report.

    Returns:
        Markdown-formatted report string.
    """
    lines: list[str] = [
        "# Domain Sensitivity Analysis",
        "",
        "Per-category help/hurt rates with Benjamini-Hochberg FDR correction.",
        "",
        "| Category | n | Help | Hurt | Help Rate | McNemar p | BH-q | Significant? |",
        "| -------- | -:| ----:| ----:| ---------:| ---------:| ----:| ------------ |",
    ]

    for cat, stats in sorted(sensitivity.items(), key=lambda x: -x[1].get("n", 0)):
        if stats.get("dropped"):
            lines.append(f"| {cat} | {stats['n']} | — | — | — | — | — | *dropped (n<2)* |")
            continue
        sig = "✓" if stats["is_significant"] else ""
        lines.append(
            f"| {cat} | {stats['n']} | {stats['help_count']} | {stats['hurt_count']} "
            f"| {stats['help_rate']:.2f} | {stats['mcnemar_p']:.4f} "
            f"| {stats['bh_q']:.4f} | {sig} |"
        )

    lines += [""]

    # Interpretation
    sig_cats = [
        c for c, s in sensitivity.items() if s.get("is_significant") and not s.get("dropped")
    ]
    if sig_cats:
        lines += [
            f"**Significant categories (BH-q < 0.05):** {', '.join(sorted(sig_cats))}",
            "",
        ]
    else:
        lines += [
            "**No categories reach significance after BH-FDR correction.**",
            "",
        ]

    report = "\n".join(lines)

    if output_path:
        from pathlib import Path

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")

    return report
