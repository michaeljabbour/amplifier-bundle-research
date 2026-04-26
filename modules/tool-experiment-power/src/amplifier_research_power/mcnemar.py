"""
mcnemar.py — McNemar paired-binary power calculations.

All three directions are supported:
  required_n_mcnemar  —  n needed for target power given effect
  mde_mcnemar         —  smallest detectable Δ (pp) at target power given n
  power_mcnemar       —  achieved power given n and effect
  sensitivity_table   —  cross-product sensitivity table as a DataFrame
"""

from __future__ import annotations

import math

import pandas as pd
from scipy import optimize
from scipy.stats import norm


def _validate_mcnemar_inputs(p_disc: float, p_help_given_disc: float) -> None:
    """Raise ValueError for out-of-range parameters."""
    if not (0.0 < p_disc < 1.0):
        raise ValueError(f"p_disc must be in (0, 1); got {p_disc}")
    if not (0.5 <= p_help_given_disc <= 1.0):
        raise ValueError(f"p_help_given_disc must be in [0.5, 1.0]; got {p_help_given_disc}")


def required_n_mcnemar(
    p_disc: float,
    p_help_given_disc: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> int:
    """Compute the required sample size for McNemar's exact paired-binary test.

    Uses the Schork-Williams (1980) approximation:

        n = [z_{α/2}·√p_disc  +  z_β·√(p_disc − Δ²)]²  /  Δ²

    where Δ = p_disc × (2·p_help_given_disc − 1)

    Parameters
    ----------
    p_disc : float
        Probability of a discordant pair = (help + hurt) / n.
    p_help_given_disc : float
        P(help | discordant). Must be > 0.5 for a "help" direction test.
    alpha : float
        Type-I error rate (default 0.05).
    power : float
        Target power 1 − β (default 0.80).
    two_sided : bool
        If True (default) use z_{α/2}; if False use z_α.

    Returns
    -------
    int
        Required sample size n (rounded up via math.ceil).
    """
    _validate_mcnemar_inputs(p_disc, p_help_given_disc)

    alpha_tail = alpha / 2 if two_sided else alpha
    z_alpha = norm.ppf(1 - alpha_tail)
    z_beta = norm.ppf(power)

    ratio = 2.0 * p_help_given_disc - 1.0  # in [0, 1]
    delta = p_disc * ratio  # = p_b - p_c (absolute accuracy gain)

    # Schork-Williams numerator & denominator
    numer = (z_alpha * math.sqrt(p_disc) + z_beta * math.sqrt(p_disc - delta**2)) ** 2
    denom = delta**2

    return math.ceil(numer / denom)


def power_mcnemar(
    n: int,
    p_disc: float,
    p_help_given_disc: float,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> float:
    """Compute achieved power for a given n and discordant pattern.

    Parameters
    ----------
    n : int
        Sample size.
    p_disc : float
        Probability of a discordant pair.
    p_help_given_disc : float
        P(help | discordant).
    alpha : float
        Type-I error rate (default 0.05).
    two_sided : bool
        If True (default) use two-sided critical value.

    Returns
    -------
    float
        Achieved power in [0, 1].
    """
    _validate_mcnemar_inputs(p_disc, p_help_given_disc)

    alpha_tail = alpha / 2 if two_sided else alpha
    z_alpha = norm.ppf(1 - alpha_tail)

    ratio = 2.0 * p_help_given_disc - 1.0
    delta = p_disc * ratio

    # Under H1 the standardised test statistic has:
    #   mean  = sqrt(n)*delta / sqrt(p_disc)
    #   var   = (p_disc - delta^2) / p_disc
    ncp = math.sqrt(n) * delta / math.sqrt(p_disc)
    sd_h1 = math.sqrt(max((p_disc - delta**2) / p_disc, 1e-12))

    # Power = Φ( (ncp - z_alpha) / sd_h1 )
    pwr = norm.cdf((ncp - z_alpha) / sd_h1)
    return float(pwr)


def mde_mcnemar(
    n: int,
    p_disc: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> float:
    """Minimum detectable effect Δ (in percentage points) for given n.

    Solves numerically for the smallest Δ (= p_disc*(2·p_help_given_disc−1))
    such that power_mcnemar(n, p_disc, p_help_given_disc) ≥ target power.

    Parameters
    ----------
    n : int
        Sample size.
    p_disc : float
        Probability of a discordant pair.
    alpha : float
        Type-I error rate (default 0.05).
    power : float
        Target power (default 0.80).
    two_sided : bool
        If True (default) use two-sided critical value.

    Returns
    -------
    float
        MDE in percentage points (i.e. Δ × 100).
    """
    if not (0.0 < p_disc < 1.0):
        raise ValueError(f"p_disc must be in (0, 1); got {p_disc}")

    # Objective: find Δ such that achieved power equals target
    def _power_minus_target(delta: float) -> float:
        if delta <= 0 or delta >= p_disc:
            return -power
        p_hgd = 0.5 + delta / (2.0 * p_disc)
        return power_mcnemar(n, p_disc, p_hgd, alpha=alpha, two_sided=two_sided) - power

    # Δ must be in (0, p_disc); use brentq
    lo = 1e-6
    hi = p_disc - 1e-6
    try:
        delta_star = float(optimize.brentq(_power_minus_target, lo, hi, xtol=1e-9))  # type: ignore[arg-type]
    except ValueError:
        # Power never reaches target; return max possible Δ
        delta_star = hi

    return delta_star * 100.0  # convert to percentage points


def sensitivity_table(
    p_disc_range: list[float],
    p_help_given_disc_range: list[float],
    target_pp: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> pd.DataFrame:
    """Build a cross-product sensitivity table of required n's.

    For each (p_disc, p_help_given_disc) combination, compute the required n
    and the implied Δ in pp.

    Parameters
    ----------
    p_disc_range : list[float]
        Values of p_disc to vary.
    p_help_given_disc_range : list[float]
        Values of p_help_given_disc to vary.
    target_pp : float
        Reference target effect in pp (included as a column for context).
    alpha : float
        Type-I error rate (default 0.05).
    power : float
        Target power (default 0.80).

    Returns
    -------
    pd.DataFrame
        Columns: p_disc, p_help_given_disc, delta_pp, required_n, target_pp.
    """
    rows = []
    for pd_val in p_disc_range:
        for phgd in p_help_given_disc_range:
            try:
                n = required_n_mcnemar(pd_val, phgd, alpha=alpha, power=power)
                delta_pp = pd_val * (2.0 * phgd - 1.0) * 100.0
                rows.append(
                    {
                        "p_disc": pd_val,
                        "p_help_given_disc": phgd,
                        "delta_pp": round(delta_pp, 2),
                        "required_n": n,
                        "target_pp": target_pp,
                    }
                )
            except ValueError:
                pass  # skip invalid combinations

    return pd.DataFrame(rows)
