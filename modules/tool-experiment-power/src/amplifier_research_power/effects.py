"""
effects.py — Effect size conversions and CI utilities.

Functions
---------
cohens_h         Cohen's h for two proportions.
risk_ratio_ci    Risk ratio with Wald CI on the log scale.
"""

from __future__ import annotations

import math

from scipy.stats import norm


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for two proportions.

    h = 2·(arcsin(√p2) − arcsin(√p1))

    A positive value indicates p2 > p1 (improvement direction).

    Parameters
    ----------
    p1 : float
        Baseline proportion, in (0, 1).
    p2 : float
        Comparison proportion, in (0, 1).

    Returns
    -------
    float
        Cohen's h effect size.
    """
    return 2.0 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))


def risk_ratio_ci(
    count1: int,
    n1: int,
    count2: int,
    n2: int,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Risk ratio with Wald CI on the log scale.

    RR = (count1/n1) / (count2/n2)

    The 95% CI (or 1-α) is constructed via the delta method:
        log(RR) ± z_{α/2} · √(1/count1 − 1/n1 + 1/count2 − 1/n2)

    Parameters
    ----------
    count1 : int
        Number of events in group 1 (numerator).
    n1 : int
        Total in group 1.
    count2 : int
        Number of events in group 2 (denominator).
    n2 : int
        Total in group 2.
    alpha : float
        Significance level (default 0.05 → 95% CI).

    Returns
    -------
    tuple[float, float, float]
        (risk_ratio, ci_lower, ci_upper)
    """
    p1 = count1 / n1
    p2 = count2 / n2

    rr = p1 / p2

    # Delta-method SE for log(RR)
    se_log_rr = math.sqrt(1.0 / count1 - 1.0 / n1 + 1.0 / count2 - 1.0 / n2)

    z = norm.ppf(1 - alpha / 2)
    log_rr = math.log(rr)

    lower = math.exp(log_rr - z * se_log_rr)
    upper = math.exp(log_rr + z * se_log_rr)

    return rr, lower, upper
