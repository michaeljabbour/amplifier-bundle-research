"""
verdict.py — Apply pre-registered thresholds to produce a block evaluation verdict.

Given a list of per-split statistics, computes:
  - Combined paired delta (McNemar-based)
  - 95% CI for combined delta
  - Per-split delta variance
  - McNemar power for observed effect
  - Verdict: WORKS | HETEROGENEOUS | DOES_NOT_WORK | UNDERPOWERED
"""

from __future__ import annotations

import math

try:
    from scipy.stats import binom as sp_binom
    from scipy.stats import binomtest

    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False
    binomtest = None  # type: ignore[assignment]
    sp_binom = None  # type: ignore[assignment]


# ─────────────────────────────────────────────────────────────────────────────
# Statistical helpers
# ─────────────────────────────────────────────────────────────────────────────


def _mcnemar_p(n_01: int, n_10: int) -> float:
    """Exact two-tailed McNemar p-value."""
    n_disc = n_01 + n_10
    if n_disc == 0:
        return 1.0
    if binomtest is not None:
        result = binomtest(max(n_01, n_10), n_disc, 0.5, alternative="greater")
        return float(min(1.0, 2.0 * float(result.pvalue)))
    z = (abs(n_01 - n_10) - 1.0) / math.sqrt(n_disc)
    return float(min(1.0, math.erfc(z / math.sqrt(2))))


def _delta_ci(n_01: int, n_10: int, n: int) -> tuple[float, float]:
    """95% CI for paired delta (n_01 - n_10)/n using normal approximation.

    Returns (ci_lower_pp, ci_upper_pp) in percentage points.
    """
    if n == 0:
        return (0.0, 0.0)
    delta = (n_01 - n_10) / n * 100.0  # percentage points
    n_disc = n_01 + n_10
    se_pp = math.sqrt(n_disc) / n * 100.0  # SE in pp
    z = 1.96  # 95% CI
    return (delta - z * se_pp, delta + z * se_pp)


def _mcnemar_power(n_01: int, n_10: int, n: int) -> float:
    """Estimate McNemar test power for the observed discordant-pair counts.

    Under the observed effect p_disc = n_01/(n_01+n_10), computes
    P(reject H0) given n_discordant trials and the exact critical value at α=0.05.

    Returns power in [0, 1].
    """
    n_disc = n_01 + n_10
    if n_disc == 0:
        return 0.0

    p_obs = n_01 / n_disc

    if not _HAS_SCIPY or sp_binom is None:
        # Fallback: normal approximation
        if p_obs <= 0.5:
            return 0.0
        se = math.sqrt(0.5 * 0.5 / n_disc)
        effect_se = (p_obs - 0.5) / se
        z_alpha = 1.96
        power = 0.5 * math.erfc(-(effect_se - z_alpha) / math.sqrt(2))
        return min(1.0, max(0.0, power))

    # Find the critical value k* such that two-tailed McNemar p(k*) ≤ 0.05.
    # k* is the smallest k where P(X >= k | n_disc, 0.5) ≤ 0.025.
    alpha = 0.05
    k_crit = n_disc + 1  # default: can never reject
    for k in range(n_disc, 0, -1):
        two_tail_p = min(1.0, 2.0 * float(sp_binom.sf(k - 1, n_disc, 0.5)))
        if two_tail_p > alpha:
            # k is too small to reject; k+1 was the last rejectable value
            k_crit = k + 1
            break

    # Power = P(X >= k_crit | n_disc, p_obs)
    power = float(sp_binom.sf(k_crit - 1, n_disc, p_obs))
    return min(1.0, max(0.0, power))


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

_HETEROGENEOUS_RANGE_PP = 3.0  # splits vary ≥ this many pp → possibly HETEROGENEOUS
_POWER_THRESHOLD = 0.80


def compute_verdict(
    splits: list[dict],
    threshold_paired_delta: float = 5.0,
    threshold_substantive_delta: float = 10.0,
    threshold_fdr: float = 0.05,
    threshold_replication_splits: int = 3,
) -> dict:
    """Apply pre-registered thresholds to yield a block evaluation verdict.

    Each element of *splits* must have:
      - ``n``: total paired items
      - ``n_01``: items where baseline wrong, treatment correct
      - ``n_10``: items where baseline correct, treatment wrong

    Verdict rules (checked in order):
    1. **UNDERPOWERED** — combined delta ≥ threshold but McNemar power < 0.80.
    2. **HETEROGENEOUS** — split deltas vary ≥ 3pp AND combined McNemar p < fdr threshold
       (statistically significant but inconsistent across splits).
    3. **WORKS** — combined delta ≥ threshold_paired_delta AND ≥
       threshold_substantive_delta AND McNemar p < threshold_fdr AND
       ≥ threshold_replication_splits splits show positive direction AND
       split range < 3pp.
    4. **DOES_NOT_WORK** — default fallback (delta too small or CI crosses zero).

    Args:
        splits: List of per-split statistics dicts.
        threshold_paired_delta: Minimum net improvement (pp) to call WORKS.
        threshold_substantive_delta: Minimum absolute delta (pp) for WORKS.
        threshold_fdr: Maximum McNemar p-value for WORKS / HETEROGENEOUS.
        threshold_replication_splits: Minimum splits with positive delta for WORKS.

    Returns:
        ``{"verdict": str, "evidence": {...}}``
    """
    if not splits:
        return {
            "verdict": "DOES_NOT_WORK",
            "evidence": {
                "reason": "no splits provided",
                "combined_delta": 0.0,
                "ci_lower": 0.0,
                "ci_upper": 0.0,
                "mcnemar_p": 1.0,
                "power_estimate": 0.0,
                "split_deltas": [],
            },
        }

    # Aggregate across splits
    total_n_01 = sum(s["n_01"] for s in splits)
    total_n_10 = sum(s["n_10"] for s in splits)
    total_n = sum(s["n"] for s in splits)

    combined_delta = ((total_n_01 - total_n_10) / total_n * 100.0) if total_n > 0 else 0.0
    ci_lower, ci_upper = _delta_ci(total_n_01, total_n_10, total_n)
    mcnemar_p = _mcnemar_p(total_n_01, total_n_10)
    power = _mcnemar_power(total_n_01, total_n_10, total_n)

    # Per-split deltas
    split_deltas = [
        ((s["n_01"] - s["n_10"]) / s["n"] * 100.0) if s["n"] > 0 else 0.0 for s in splits
    ]

    # Number of splits with positive direction
    n_positive_splits = sum(1 for d in split_deltas if d > 0)

    # Delta range across splits
    split_range = (max(split_deltas) - min(split_deltas)) if len(split_deltas) > 1 else 0.0

    evidence = {
        "combined_delta": combined_delta,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "mcnemar_p": mcnemar_p,
        "power_estimate": power,
        "split_deltas": split_deltas,
        "split_range_pp": split_range,
        "n_positive_splits": n_positive_splits,
        "total_n_01": total_n_01,
        "total_n_10": total_n_10,
        "total_n": total_n,
    }

    # ── Rule 1: UNDERPOWERED ──────────────────────────────────────────────
    # Only check power when the delta looks interesting (above threshold)
    # but the test lacks statistical resolution to confirm it.
    if combined_delta >= threshold_paired_delta and power < _POWER_THRESHOLD:
        return {"verdict": "UNDERPOWERED", "evidence": evidence}

    # ── Rule 2: HETEROGENEOUS ─────────────────────────────────────────────
    # Effect is statistically real (p < fdr) but inconsistent across splits.
    # Check BEFORE the delta-threshold gate — heterogeneity can exist even when
    # combined delta doesn't clear the substantive threshold.
    if split_range >= _HETEROGENEOUS_RANGE_PP and mcnemar_p < threshold_fdr:
        return {"verdict": "HETEROGENEOUS", "evidence": evidence}

    # ── Rule 3: WORKS ────────────────────────────────────────────────────
    if (
        combined_delta >= threshold_paired_delta
        and combined_delta >= threshold_substantive_delta
        and mcnemar_p < threshold_fdr
        and n_positive_splits >= threshold_replication_splits
        and ci_lower >= 0
    ):
        return {"verdict": "WORKS", "evidence": evidence}

    # ── Rule 4: DOES_NOT_WORK ─────────────────────────────────────────────
    return {"verdict": "DOES_NOT_WORK", "evidence": evidence}
