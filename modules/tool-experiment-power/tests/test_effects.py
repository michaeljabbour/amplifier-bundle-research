"""
Tests for effects.py — effect size conversions and CI utilities.

TDD RED phase: all tests reference amplifier_research_power.effects functions
that do not yet exist.
"""
from __future__ import annotations

import math

import pytest


# ---------------------------------------------------------------------------
# Test 1: Cohen's h — 2*(arcsin(sqrt(p2)) - arcsin(sqrt(p1)))
# ---------------------------------------------------------------------------


def test_pp_to_cohens_h_proportions() -> None:
    """cohens_h(p1, p2) == 2*(arcsin(sqrt(p2)) - arcsin(sqrt(p1)))."""
    from amplifier_research_power.effects import cohens_h

    p1, p2 = 0.50, 0.55  # 5 pp improvement
    expected = 2 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))
    result = cohens_h(p1, p2)
    assert abs(result - expected) < 1e-10, f"cohens_h mismatch: {result} vs {expected}"


def test_cohens_h_sign_convention() -> None:
    """cohens_h(p1, p2) > 0 when p2 > p1 (improvement direction)."""
    from amplifier_research_power.effects import cohens_h

    assert cohens_h(0.40, 0.50) > 0
    assert cohens_h(0.50, 0.40) < 0
    assert abs(cohens_h(0.40, 0.40)) < 1e-12


# ---------------------------------------------------------------------------
# Test 2: risk_ratio_ci — Wald CI for log(RR)
# ---------------------------------------------------------------------------


def test_risk_ratio_with_ci() -> None:
    """risk_ratio_ci returns (rr, lower, upper) with lower < rr < upper."""
    from amplifier_research_power.effects import risk_ratio_ci

    rr, lower, upper = risk_ratio_ci(count1=60, n1=100, count2=40, n2=100, alpha=0.05)

    # RR should be 60/40 = 1.5
    assert abs(rr - 1.5) < 1e-10, f"Expected RR=1.5, got {rr}"
    # CI should bracket the point estimate
    assert lower < rr < upper, f"CI [{lower:.3f}, {upper:.3f}] does not bracket {rr:.3f}"
    # Wald CI for log(RR): 95% CI for RR = 1.5 should be roughly [1.1, 2.0]
    assert lower > 1.0, f"Lower CI {lower:.3f} should be > 1.0"
    assert upper < 3.0, f"Upper CI {upper:.3f} should be < 3.0"


# ---------------------------------------------------------------------------
# Test 3: pp ↔ Cohen's h round-trip consistency
# ---------------------------------------------------------------------------


def test_pp_round_trip() -> None:
    """Converting pp → Cohen's h and back should recover original proportions.

    If h = cohens_h(p1, p2), then p2 = sin(arcsin(sqrt(p1)) + h/2)^2.
    """
    from amplifier_research_power.effects import cohens_h

    p1 = 0.45
    p2 = 0.55
    h = cohens_h(p1, p2)

    # Recover p2 from h and p1
    recovered_p2 = math.sin(math.asin(math.sqrt(p1)) + h / 2) ** 2
    assert abs(recovered_p2 - p2) < 1e-10, (
        f"Round-trip failed: p2={p2}, recovered={recovered_p2}"
    )
