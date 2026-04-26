"""
Tests for ttest.py — independent t-test power analysis.

TDD RED phase: all tests reference amplifier_research_power.ttest functions
that do not yet exist.
"""
from __future__ import annotations

import math


# ---------------------------------------------------------------------------
# Test 1: required_n_ttest matches statsmodels reference
# ---------------------------------------------------------------------------


def test_required_n_ttest_matches_statsmodels() -> None:
    """required_n_ttest should agree with statsmodels.tt_ind_solve_power."""
    from statsmodels.stats.power import tt_ind_solve_power

    from amplifier_research_power.ttest import required_n_ttest

    cohens_d = 0.5
    alpha = 0.05
    power = 0.80

    n_ours = required_n_ttest(cohens_d=cohens_d, alpha=alpha, power=power)
    n_sm = tt_ind_solve_power(effect_size=cohens_d, alpha=alpha, power=power, alternative="two-sided")
    n_sm_ceil = math.ceil(n_sm)

    # Must be an integer
    assert isinstance(n_ours, int), f"expected int, got {type(n_ours)}"
    # Must agree with statsmodels within 1 (rounding)
    assert abs(n_ours - n_sm_ceil) <= 1, (
        f"Our n={n_ours} disagrees with statsmodels ceil({n_sm:.2f})={n_sm_ceil}"
    )


def test_required_n_ttest_increases_with_smaller_d() -> None:
    """Smaller Cohen's d requires more participants."""
    from amplifier_research_power.ttest import required_n_ttest

    n_small = required_n_ttest(cohens_d=0.2)
    n_medium = required_n_ttest(cohens_d=0.5)
    n_large = required_n_ttest(cohens_d=0.8)
    assert n_small > n_medium > n_large, (
        f"n should decrease with effect size: {n_small}, {n_medium}, {n_large}"
    )


# ---------------------------------------------------------------------------
# Test 2: power_ttest matches statsmodels reference
# ---------------------------------------------------------------------------


def test_power_ttest_matches_statsmodels() -> None:
    """power_ttest should agree with statsmodels.tt_ind_solve_power."""
    from statsmodels.stats.power import tt_ind_solve_power

    from amplifier_research_power.ttest import power_ttest

    n_per_group = 64
    cohens_d = 0.5
    alpha = 0.05

    our_power = power_ttest(n_per_group=n_per_group, cohens_d=cohens_d, alpha=alpha)
    sm_power = tt_ind_solve_power(
        effect_size=cohens_d,
        nobs1=n_per_group,
        alpha=alpha,
        alternative="two-sided",
    )

    assert isinstance(our_power, float), f"expected float, got {type(our_power)}"
    assert abs(our_power - sm_power) < 1e-6, (
        f"Our power={our_power:.6f} disagrees with statsmodels {sm_power:.6f}"
    )


def test_mde_ttest_returns_positive_float() -> None:
    """mde_ttest should return a positive Cohen's d."""
    from amplifier_research_power.ttest import mde_ttest

    d = mde_ttest(n_per_group=100, alpha=0.05, power=0.80)
    assert isinstance(d, float), f"expected float, got {type(d)}"
    assert d > 0, f"MDE should be positive, got {d}"
