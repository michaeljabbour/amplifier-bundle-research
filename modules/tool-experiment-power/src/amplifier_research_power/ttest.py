"""
ttest.py — Independent two-sample t-test power calculations (Cohen's d based).

Wraps statsmodels.stats.power.tt_ind_solve_power for consistent results.
"""

from __future__ import annotations

import math

from statsmodels.stats.power import tt_ind_solve_power


def required_n_ttest(
    cohens_d: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Required n per group for an independent two-sample t-test.

    Parameters
    ----------
    cohens_d : float
        Effect size (Cohen's d = |μ1 − μ2| / σ_pooled).
    alpha : float
        Type-I error rate (default 0.05).
    power : float
        Target power 1 − β (default 0.80).

    Returns
    -------
    int
        Required n per group (rounded up).
    """
    n_float = tt_ind_solve_power(
        effect_size=cohens_d,
        alpha=alpha,
        power=power,
        alternative="two-sided",
    )
    return math.ceil(n_float)


def power_ttest(
    n_per_group: int,
    cohens_d: float,
    alpha: float = 0.05,
) -> float:
    """Compute achieved power for a two-sample t-test.

    Parameters
    ----------
    n_per_group : int
        Sample size per group.
    cohens_d : float
        Effect size (Cohen's d).
    alpha : float
        Type-I error rate (default 0.05).

    Returns
    -------
    float
        Achieved power in [0, 1].
    """
    pwr = tt_ind_solve_power(
        effect_size=cohens_d,
        nobs1=n_per_group,
        alpha=alpha,
        alternative="two-sided",
    )
    return float(pwr)


def mde_ttest(
    n_per_group: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Minimum detectable effect (Cohen's d) for a two-sample t-test.

    Parameters
    ----------
    n_per_group : int
        Sample size per group.
    alpha : float
        Type-I error rate (default 0.05).
    power : float
        Target power (default 0.80).

    Returns
    -------
    float
        Minimum detectable Cohen's d.
    """
    d = tt_ind_solve_power(
        nobs1=n_per_group,
        alpha=alpha,
        power=power,
        alternative="two-sided",
    )
    return float(d)
