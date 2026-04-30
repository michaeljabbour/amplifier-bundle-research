"""Calibration metrics: Expected Calibration Error (ECE), Brier score,
reliability binning. Computes the metrics described in
context/experiment-calibration-awareness.md.

Inputs are (confidence, correct) pairs:
  confidence  ∈ [0, 1]
  correct     ∈ {0, 1}

ECE (size-weighted average vertical distance from the diagonal):
  ECE = sum_b (n_b / N) * |conf_b - acc_b|
where bins are equal-width over [0, 1].

Brier score (mean squared error between confidence and outcome):
  BS = (1/N) * sum_i (confidence_i - correct_i)^2

Reliability diagram data: per-bin (n, mean_conf, mean_acc, gap).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence


@dataclass
class CalibrationBin:
    bin_index: int
    lo: float
    hi: float
    n: int
    mean_confidence: float | None
    mean_accuracy: float | None
    gap: float | None       # |mean_confidence - mean_accuracy|


@dataclass
class CalibrationReport:
    n: int
    n_bins: int
    ece: float
    brier: float
    bins: list[CalibrationBin]


def _validate_pairs(confidences: Sequence[float], corrects: Sequence[int]) -> None:
    if len(confidences) != len(corrects):
        raise ValueError(
            f"confidences and corrects must have the same length; got "
            f"{len(confidences)} and {len(corrects)}"
        )
    if not confidences:
        raise ValueError("input is empty")
    for i, c in enumerate(confidences):
        if not (0.0 <= c <= 1.0):
            raise ValueError(f"confidence[{i}] = {c} not in [0, 1]")
    for i, c in enumerate(corrects):
        if c not in (0, 1, True, False):
            raise ValueError(f"correct[{i}] = {c} not in {{0, 1}}")


def expected_calibration_error(
    confidences: Sequence[float],
    corrects: Sequence[int],
    n_bins: int = 10,
) -> float:
    """Compute the Expected Calibration Error.

    ECE = sum_b (n_b / N) * |conf_b - acc_b|

    Equal-width bins on [0, 1]. Empty bins contribute 0.
    """
    _validate_pairs(confidences, corrects)
    if n_bins < 1:
        raise ValueError(f"n_bins must be >= 1; got {n_bins}")

    n_total = len(confidences)
    bin_width = 1.0 / n_bins
    bin_sums_conf = [0.0] * n_bins
    bin_sums_correct = [0.0] * n_bins
    bin_counts = [0] * n_bins

    for c, y in zip(confidences, corrects):
        # Use min(.., n_bins-1) so that confidence == 1.0 falls in last bin
        b = min(int(c / bin_width), n_bins - 1)
        bin_sums_conf[b] += c
        bin_sums_correct[b] += float(y)
        bin_counts[b] += 1

    ece = 0.0
    for b in range(n_bins):
        if bin_counts[b] == 0:
            continue
        mean_conf = bin_sums_conf[b] / bin_counts[b]
        mean_acc = bin_sums_correct[b] / bin_counts[b]
        ece += (bin_counts[b] / n_total) * abs(mean_conf - mean_acc)

    return ece


def brier_score(
    confidences: Sequence[float],
    corrects: Sequence[int],
) -> float:
    """Mean squared error between confidence and outcome."""
    _validate_pairs(confidences, corrects)
    n = len(confidences)
    return sum((c - float(y)) ** 2 for c, y in zip(confidences, corrects)) / n


def reliability_bins(
    confidences: Sequence[float],
    corrects: Sequence[int],
    n_bins: int = 10,
) -> list[CalibrationBin]:
    """Return per-bin reliability data for a reliability diagram."""
    _validate_pairs(confidences, corrects)
    if n_bins < 1:
        raise ValueError(f"n_bins must be >= 1; got {n_bins}")

    bin_width = 1.0 / n_bins
    bin_sums_conf = [0.0] * n_bins
    bin_sums_correct = [0.0] * n_bins
    bin_counts = [0] * n_bins

    for c, y in zip(confidences, corrects):
        b = min(int(c / bin_width), n_bins - 1)
        bin_sums_conf[b] += c
        bin_sums_correct[b] += float(y)
        bin_counts[b] += 1

    out: list[CalibrationBin] = []
    for b in range(n_bins):
        lo = b * bin_width
        hi = (b + 1) * bin_width
        if bin_counts[b] == 0:
            out.append(CalibrationBin(
                bin_index=b, lo=lo, hi=hi, n=0,
                mean_confidence=None, mean_accuracy=None, gap=None,
            ))
        else:
            mc = bin_sums_conf[b] / bin_counts[b]
            ma = bin_sums_correct[b] / bin_counts[b]
            out.append(CalibrationBin(
                bin_index=b, lo=lo, hi=hi, n=bin_counts[b],
                mean_confidence=mc, mean_accuracy=ma, gap=abs(mc - ma),
            ))
    return out


def calibration_report(
    confidences: Sequence[float],
    corrects: Sequence[int],
    n_bins: int = 10,
) -> CalibrationReport:
    """Compute ECE, Brier, and reliability bins in one call."""
    _validate_pairs(confidences, corrects)
    return CalibrationReport(
        n=len(confidences),
        n_bins=n_bins,
        ece=expected_calibration_error(confidences, corrects, n_bins=n_bins),
        brier=brier_score(confidences, corrects),
        bins=reliability_bins(confidences, corrects, n_bins=n_bins),
    )


def calibration_report_to_dict(rep: CalibrationReport) -> dict:
    """Convert a CalibrationReport to a JSON-serializable dict."""
    return {
        "n": rep.n,
        "n_bins": rep.n_bins,
        "ece": rep.ece,
        "brier": rep.brier,
        "reliability_bins": [asdict(b) for b in rep.bins],
    }
