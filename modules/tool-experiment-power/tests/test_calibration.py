"""Tests for calibration module: ECE, Brier, reliability bins."""

import pytest

from amplifier_research_power.calibration import (
    CalibrationBin,
    brier_score,
    calibration_report,
    calibration_report_to_dict,
    expected_calibration_error,
    reliability_bins,
)


# -----------------------------------------------------------------
# Validation
# -----------------------------------------------------------------

def test_validation_empty_input():
    with pytest.raises(ValueError, match="empty"):
        expected_calibration_error([], [])


def test_validation_length_mismatch():
    with pytest.raises(ValueError, match="same length"):
        expected_calibration_error([0.5, 0.6], [1])


def test_validation_confidence_out_of_range():
    with pytest.raises(ValueError, match="confidence"):
        expected_calibration_error([1.5], [1])


def test_validation_correct_not_binary():
    with pytest.raises(ValueError, match="correct"):
        expected_calibration_error([0.5], [2])


def test_validation_n_bins_lt_1():
    with pytest.raises(ValueError, match="n_bins"):
        expected_calibration_error([0.5], [1], n_bins=0)


# -----------------------------------------------------------------
# ECE: edge cases
# -----------------------------------------------------------------

def test_ece_perfect_calibration_all_correct_high_conf():
    """100% confidence, 100% correct -> ECE = 0."""
    n = 100
    conf = [1.0] * n
    correct = [1] * n
    assert expected_calibration_error(conf, correct) == pytest.approx(0.0)


def test_ece_perfect_calibration_all_wrong_zero_conf():
    """0% confidence, 0% correct -> ECE = 0 (well-calibrated zero
    confidence; all in bin 0 with mean 0 conf and mean 0 acc)."""
    conf = [0.0] * 50
    correct = [0] * 50
    assert expected_calibration_error(conf, correct) == pytest.approx(0.0)


def test_ece_maximally_overconfident():
    """100% confidence, 0% correct -> ECE = 1.0 (all in last bin)."""
    conf = [0.99] * 100
    correct = [0] * 100
    # bin contains all 100; mean_conf=0.99, mean_acc=0.0 -> gap=0.99
    # weighted by n_b/N=1.0 -> ECE=0.99
    assert expected_calibration_error(conf, correct) == pytest.approx(0.99, abs=0.01)


def test_ece_maximally_underconfident():
    """1% confidence, 100% correct -> ECE close to 1.0."""
    conf = [0.01] * 100
    correct = [1] * 100
    assert expected_calibration_error(conf, correct) == pytest.approx(0.99, abs=0.01)


def test_ece_pse_v4d_worked_example():
    """Reproduces the worked example from
    context/experiment-calibration-awareness.md:
      bin 0.6-0.7: n=2,  mean_conf=0.66, mean_acc=0.50 -> gap 0.16
      bin 0.7-0.8: n=8,  mean_conf=0.74, mean_acc=0.62 -> gap 0.12
      bin 0.8-0.9: n=17, mean_conf=0.84, mean_acc=0.76 -> gap 0.08
      bin 0.9-1.0: n=15, mean_conf=0.94, mean_acc=0.93 -> gap 0.01
    ECE = (2/42)(0.16) + (8/42)(0.12) + (17/42)(0.08) + (15/42)(0.01)
        = 0.069 (approximately)
    """
    # Construct items so each bin has the specified mean_conf and mean_acc
    conf = (
        [0.66, 0.66] +              # bin 0.6-0.7, n=2
        [0.74] * 8 +                # bin 0.7-0.8, n=8
        [0.84] * 17 +               # bin 0.8-0.9, n=17
        [0.94] * 15                 # bin 0.9-1.0, n=15
    )
    correct = (
        [1, 0] +                    # n=2, mean_acc 0.50
        [1] * 5 + [0] * 3 +         # n=8, mean_acc ~0.625 (closest int outcomes -> 0.625)
        [1] * 13 + [0] * 4 +        # n=17, mean_acc ~0.765 -> nudge to 13/17=0.7647
        [1] * 14 + [0] * 1          # n=15, mean_acc ~0.933
    )
    assert len(conf) == len(correct) == 42
    ece = expected_calibration_error(conf, correct, n_bins=10)
    # Working: (2/42)*|0.66-0.50| + (8/42)*|0.74-0.625| + (17/42)*|0.84-0.7647| + (15/42)*|0.94-0.9333|
    #        = 0.0476*0.16 + 0.190*0.115 + 0.405*0.0753 + 0.357*0.0067
    #        = 0.00762 + 0.02190 + 0.03046 + 0.00239 = 0.0624
    assert ece == pytest.approx(0.062, abs=0.005)


# -----------------------------------------------------------------
# Brier
# -----------------------------------------------------------------

def test_brier_perfect():
    """All correct with confidence 1, all wrong with confidence 0 -> Brier = 0."""
    assert brier_score([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0]) == pytest.approx(0.0)


def test_brier_maximally_wrong():
    """100% confident wrong -> Brier = 1.0."""
    assert brier_score([1.0] * 10, [0] * 10) == pytest.approx(1.0)


def test_brier_uniform_random():
    """50% confidence -> Brier = 0.25 regardless of outcomes."""
    n = 100
    half = n // 2
    assert brier_score([0.5] * n, [1] * half + [0] * half) == pytest.approx(0.25)


# -----------------------------------------------------------------
# Reliability bins
# -----------------------------------------------------------------

def test_reliability_bins_empty_bins_recorded():
    """Bins with n=0 are returned with None means and gap."""
    bins = reliability_bins([0.5] * 10, [1] * 10, n_bins=10)
    assert len(bins) == 10
    # Bin 5 (0.5-0.6) should have all 10 items
    bin_5 = bins[5]
    assert bin_5.n == 10
    assert bin_5.mean_confidence == pytest.approx(0.5)
    assert bin_5.mean_accuracy == pytest.approx(1.0)
    # Other bins are empty
    for b in bins:
        if b.bin_index != 5:
            assert b.n == 0
            assert b.mean_confidence is None


def test_reliability_bins_confidence_one_in_last_bin():
    """Edge case: confidence exactly 1.0 falls in last bin, not out-of-bounds."""
    bins = reliability_bins([1.0, 1.0], [1, 0], n_bins=10)
    last = bins[-1]
    assert last.n == 2
    assert last.mean_confidence == pytest.approx(1.0)
    assert last.mean_accuracy == pytest.approx(0.5)


# -----------------------------------------------------------------
# Full report
# -----------------------------------------------------------------

def test_calibration_report_round_trip_to_dict():
    rep = calibration_report([0.5, 0.7, 0.9], [1, 1, 0])
    d = calibration_report_to_dict(rep)
    assert d["n"] == 3
    assert d["n_bins"] == 10
    assert "ece" in d
    assert "brier" in d
    assert "reliability_bins" in d
    assert len(d["reliability_bins"]) == 10
