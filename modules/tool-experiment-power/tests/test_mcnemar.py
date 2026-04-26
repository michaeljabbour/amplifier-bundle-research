"""
Tests for mcnemar.py — McNemar paired binary power analysis.

TDD RED phase: all tests reference amplifier_research_power.mcnemar functions
that do not yet exist. Expect ImportError or AttributeError on first run.
"""
from __future__ import annotations

import math

import pytest


# ---------------------------------------------------------------------------
# Test 1: required_n returns an integer
# ---------------------------------------------------------------------------


def test_required_n_returns_integer() -> None:
    """required_n_mcnemar should return a plain Python int."""
    from amplifier_research_power.mcnemar import required_n_mcnemar

    n = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.70)
    assert isinstance(n, int), f"expected int, got {type(n)}"
    assert n > 0


# ---------------------------------------------------------------------------
# Test 2: monotonic in effect size (smaller Δ → larger n)
# ---------------------------------------------------------------------------


def test_required_n_increases_with_smaller_effect() -> None:
    """Smaller p_help_given_disc (weaker imbalance) requires more participants."""
    from amplifier_research_power.mcnemar import required_n_mcnemar

    # p_disc fixed; higher p_help_given_disc = stronger imbalance = smaller n
    n_small_effect = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.55)
    n_large_effect = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.80)
    assert n_small_effect > n_large_effect, (
        f"n for p_help=0.55 ({n_small_effect}) should exceed n for p_help=0.80 ({n_large_effect})"
    )


# ---------------------------------------------------------------------------
# Test 3: monotonic in alpha (smaller α → larger n)
# ---------------------------------------------------------------------------


def test_required_n_increases_with_smaller_alpha() -> None:
    """Stricter α=0.01 requires more participants than α=0.05."""
    from amplifier_research_power.mcnemar import required_n_mcnemar

    n_alpha_01 = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.70, alpha=0.01)
    n_alpha_05 = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.70, alpha=0.05)
    assert n_alpha_01 > n_alpha_05, (
        f"n for α=0.01 ({n_alpha_01}) should exceed n for α=0.05 ({n_alpha_05})"
    )


# ---------------------------------------------------------------------------
# Test 4: monotonic in power (higher power → larger n)
# ---------------------------------------------------------------------------


def test_required_n_increases_with_higher_power() -> None:
    """Higher target power requires more participants."""
    from amplifier_research_power.mcnemar import required_n_mcnemar

    n_80 = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.70, power=0.80)
    n_95 = required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.70, power=0.95)
    assert n_95 > n_80, f"n for power=0.95 ({n_95}) should exceed n for power=0.80 ({n_80})"


# ---------------------------------------------------------------------------
# Test 5: input validation raises ValueError for bad ranges
# ---------------------------------------------------------------------------


def test_required_n_validates_input_ranges() -> None:
    """Out-of-range inputs should raise ValueError."""
    from amplifier_research_power.mcnemar import required_n_mcnemar

    # p_disc must be in (0, 1)
    with pytest.raises(ValueError, match="p_disc"):
        required_n_mcnemar(p_disc=0.0, p_help_given_disc=0.70)

    with pytest.raises(ValueError, match="p_disc"):
        required_n_mcnemar(p_disc=1.0, p_help_given_disc=0.70)

    # p_help_given_disc must be in [0.5, 1.0]
    with pytest.raises(ValueError, match="p_help_given_disc"):
        required_n_mcnemar(p_disc=0.20, p_help_given_disc=0.40)

    with pytest.raises(ValueError, match="p_help_given_disc"):
        required_n_mcnemar(p_disc=0.20, p_help_given_disc=1.1)


# ---------------------------------------------------------------------------
# Test 6: known reference value (manually verified via Schork-Williams formula)
# ---------------------------------------------------------------------------


def test_known_textbook_value() -> None:
    """Verify against a hand-computed reference for well-chosen inputs.

    p_disc = 0.30, p_help_given_disc = 0.70, alpha = 0.05, power = 0.80:
      ratio = 2*0.70 - 1 = 0.40
      Δ     = 0.30 * 0.40 = 0.12
      n_exact ≈ 161.2  →  ceil = 162
    """
    from amplifier_research_power.mcnemar import required_n_mcnemar

    n = required_n_mcnemar(p_disc=0.30, p_help_given_disc=0.70, alpha=0.05, power=0.80)
    # Accept ±2 to accommodate slight floating-point differences
    assert 160 <= n <= 164, f"Expected n ≈ 162 for textbook inputs, got {n}"


# ---------------------------------------------------------------------------
# Test 7: mde_mcnemar round-trip with required_n_mcnemar
# ---------------------------------------------------------------------------


def test_mde_consistency_with_required_n() -> None:
    """Round-trip: solve for n given Δ, then compute MDE for that n — must match.

    If required_n gives n for p_help_given_disc Q, then mde_mcnemar(n, p_disc)
    should return ≈ p_disc*(2Q-1)*100 pp (the Δ used to get that n).
    Because n is rounded up, the MDE should be ≤ the original Δ.
    """
    from amplifier_research_power.mcnemar import mde_mcnemar, required_n_mcnemar

    p_disc = 0.20
    p_help_given_disc = 0.75
    alpha = 0.05
    power = 0.80

    expected_delta_pp = p_disc * (2 * p_help_given_disc - 1) * 100  # ≈ 10 pp

    n = required_n_mcnemar(p_disc=p_disc, p_help_given_disc=p_help_given_disc, alpha=alpha, power=power)
    mde_pp = mde_mcnemar(n=n, p_disc=p_disc, alpha=alpha, power=power)

    # MDE should be close to the original Δ (within 0.5 pp tolerance)
    assert abs(mde_pp - expected_delta_pp) < 0.5, (
        f"Round-trip MDE {mde_pp:.3f} pp differs from expected {expected_delta_pp:.3f} pp by more than 0.5 pp"
    )


# ---------------------------------------------------------------------------
# Extra tests for power_mcnemar (post-hoc power)
# ---------------------------------------------------------------------------


def test_power_mcnemar_increases_with_n() -> None:
    """Larger sample → higher achieved power."""
    from amplifier_research_power.mcnemar import power_mcnemar

    p1 = power_mcnemar(n=100, p_disc=0.20, p_help_given_disc=0.70, alpha=0.05)
    p2 = power_mcnemar(n=300, p_disc=0.20, p_help_given_disc=0.70, alpha=0.05)
    assert p2 > p1, f"Power should increase with n: got {p1:.3f} (n=100) vs {p2:.3f} (n=300)"


def test_sensitivity_table_returns_dataframe() -> None:
    """sensitivity_table should return a pandas DataFrame with expected columns."""
    import pandas as pd

    from amplifier_research_power.mcnemar import sensitivity_table

    df = sensitivity_table(
        p_disc_range=[0.10, 0.15],
        p_help_given_disc_range=[0.60, 0.70],
        target_pp=5,
        alpha=0.05,
        power=0.80,
    )
    assert isinstance(df, pd.DataFrame), "Expected pandas DataFrame"
    assert len(df) == 4, f"Expected 2×2 = 4 rows, got {len(df)}"
    for col in ("p_disc", "p_help_given_disc", "required_n", "delta_pp"):
        assert col in df.columns, f"Missing column: {col}"
