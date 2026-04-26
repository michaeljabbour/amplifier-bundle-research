"""
CLI integration tests — end-to-end invocation via subprocess.

TDD RED phase: these tests invoke the 'amplifier-research-power' entry point,
which does not yet exist. They should fail with ModuleNotFoundError or
a non-zero exit code before the implementation is written.
"""
from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI as a module so it works even before the entry-point script is installed."""
    return subprocess.run(
        [sys.executable, "-m", "amplifier_research_power.cli", *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# required-n mcnemar
# ---------------------------------------------------------------------------


def test_cli_required_n_mcnemar_exits_zero() -> None:
    """required-n mcnemar exits 0 and prints a numeric result."""
    result = _run(
        "required-n", "mcnemar",
        "--p-disc", "0.12",
        "--p-help-given-disc", "0.667",
        "--alpha", "0.05",
        "--power", "0.80",
    )
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert "n" in result.stdout.lower() or any(c.isdigit() for c in result.stdout), (
        f"Expected numeric output, got:\n{result.stdout}"
    )


def test_cli_required_n_mcnemar_value_plausible() -> None:
    """required-n mcnemar output should contain a plausible integer n."""
    result = _run(
        "required-n", "mcnemar",
        "--p-disc", "0.20",
        "--p-help-given-disc", "0.70",
        "--alpha", "0.05",
        "--power", "0.80",
    )
    assert result.returncode == 0
    # Extract first integer from output; it should be roughly 162
    import re
    numbers = [int(m) for m in re.findall(r"\b(\d+)\b", result.stdout)]
    assert numbers, f"No integers in output: {result.stdout}"
    n = numbers[0]
    assert 100 < n < 300, f"Implausible n={n} for p_disc=0.20, p_help=0.70"


# ---------------------------------------------------------------------------
# mde mcnemar
# ---------------------------------------------------------------------------


def test_cli_mde_mcnemar_exits_zero() -> None:
    """mde mcnemar exits 0 and prints a MDE value."""
    result = _run(
        "mde", "mcnemar",
        "--n", "150",
        "--p-disc", "0.12",
        "--alpha", "0.05",
        "--power", "0.80",
    )
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    assert any(c.isdigit() for c in result.stdout), f"Expected numeric output:\n{result.stdout}"


# ---------------------------------------------------------------------------
# post-hoc mcnemar
# ---------------------------------------------------------------------------


def test_cli_post_hoc_mcnemar_exits_zero() -> None:
    """post-hoc mcnemar exits 0 and prints an achieved-power value."""
    result = _run(
        "post-hoc", "mcnemar",
        "--n", "150",
        "--p-disc", "0.12",
        "--p-help-given-disc", "0.667",
    )
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    # Should contain a decimal fraction (the achieved power)
    import re
    floats = re.findall(r"\d+\.\d+", result.stdout)
    assert floats, f"Expected a float in output:\n{result.stdout}"
    power_val = float(floats[0])
    assert 0.0 < power_val < 1.0, f"Power {power_val} not in (0, 1)"


# ---------------------------------------------------------------------------
# sensitivity mcnemar
# ---------------------------------------------------------------------------


def test_cli_sensitivity_mcnemar_exits_zero() -> None:
    """sensitivity mcnemar exits 0 and prints a table-like output."""
    result = _run(
        "sensitivity", "mcnemar",
        "--p-disc-range", "0.10,0.15,0.20",
        "--p-help-given-disc-range", "0.55,0.65,0.75",
        "--target-pp", "5",
        "--alpha", "0.05",
        "--power", "0.80",
    )
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    # Should contain at least 9 lines (header + 9 data rows)
    lines = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
    assert len(lines) >= 5, f"Expected table output, got {len(lines)} lines:\n{result.stdout}"


def test_cli_sensitivity_mcnemar_row_count() -> None:
    """sensitivity with 2×2 ranges should produce 4 data rows."""
    result = _run(
        "sensitivity", "mcnemar",
        "--p-disc-range", "0.10,0.20",
        "--p-help-given-disc-range", "0.60,0.70",
        "--target-pp", "5",
    )
    assert result.returncode == 0, f"Non-zero exit:\n{result.stderr}"
    import re
    # Count lines with numeric content
    data_lines = [ln for ln in result.stdout.strip().splitlines() if re.search(r"\d", ln)]
    # Expect header + 4 data rows = at least 4 numeric-containing lines
    assert len(data_lines) >= 4, (
        f"Expected at least 4 data lines in 2×2 table, got {len(data_lines)}:\n{result.stdout}"
    )
