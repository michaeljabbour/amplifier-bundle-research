"""
TDD RED phase — test_cli_integration.py

End-to-end CLI integration test.
Invokes `amplifier-research-stage-analyzer` as a subprocess using the module
entry point.  All tests MUST FAIL before implementation exists.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI as a module so it works even before the entry-point script is installed."""
    return subprocess.run(
        [sys.executable, "-m", "amplifier_research_stage_analyzer.cli", *args],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


def _make_synthetic_traces(tmp_path: Path) -> Path:
    """Write a 10-record synthetic stage_traces.jsonl covering all categories."""
    records = []

    def gen(length: int, is_empty: bool = False) -> dict:
        return {
            "output": "x" * length,
            "output_length": length,
            "latency_ms": 1000.0,
            "cost_usd": 0.001,
            "is_empty": is_empty,
            "is_truncated": False,
        }

    def critic(length: int, is_empty: bool = False, verdict: str = "keep") -> dict:
        return {
            "output": "y" * length,
            "output_length": length,
            "latency_ms": 800.0,
            "cost_usd": 0.0008,
            "is_empty": is_empty,
            "verdict": verdict,
        }

    def revert(selected_stage: str = "generator", reason: str = "gen_better") -> dict:
        return {
            "selected_stage": selected_stage,
            "selected_response": "text",
            "reason": reason,
        }

    # 3x gen_substantive_critic_empty (final_is_empty=True)
    for i in range(3):
        records.append({
            "item_id": f"gsce_{i:03d}",
            "approach_id": "A1",
            "approach_name": "Reflection",
            "stages": {
                "generator": gen(200),
                "critic": critic(0, is_empty=True),
                "revert_decision": revert(reason="both_empty"),
            },
            "final_response_length": 0,
            "final_is_empty": True,
            "timestamp": "2024-01-01T00:00:00Z",
        })

    # 2x gen_substantive_critic_substantive (final_is_empty=True)
    for i in range(2):
        records.append({
            "item_id": f"gscs_{i:03d}",
            "approach_id": "A1",
            "approach_name": "Reflection",
            "stages": {
                "generator": gen(200),
                "critic": critic(150, verdict="revise"),
                "revert_decision": revert(reason="critic_revise"),
            },
            "final_response_length": 0,
            "final_is_empty": True,
            "timestamp": "2024-01-01T00:00:00Z",
        })

    # 2x gen_empty_critic_empty (final_is_empty=True)
    for i in range(2):
        records.append({
            "item_id": f"gece_{i:03d}",
            "approach_id": "A1",
            "approach_name": "Reflection",
            "stages": {
                "generator": gen(0, is_empty=True),
                "critic": critic(0, is_empty=True, verdict="abstain"),
                "revert_decision": revert(reason="both_empty"),
            },
            "final_response_length": 0,
            "final_is_empty": True,
            "timestamp": "2024-01-01T00:00:00Z",
        })

    # 2x gen_empty_critic_substantive (final_is_empty=True)
    for i in range(2):
        records.append({
            "item_id": f"gecs_{i:03d}",
            "approach_id": "A1",
            "approach_name": "Reflection",
            "stages": {
                "generator": gen(0, is_empty=True),
                "critic": critic(150),
                "revert_decision": revert(selected_stage="generator", reason="gen_better"),
            },
            "final_response_length": 0,
            "final_is_empty": True,
            "timestamp": "2024-01-01T00:00:00Z",
        })

    # 1x A0-style non-empty record (should NOT be categorized as empty)
    records.append({
        "item_id": "a0_ok_001",
        "approach_id": "A0",
        "approach_name": "Baseline",
        "stages": {
            "generator": gen(300),
            "critic": None,
            "revert_decision": None,
        },
        "final_response_length": 300,
        "final_is_empty": False,
        "timestamp": "2024-01-01T00:00:00Z",
    })

    fpath = tmp_path / "stage_traces.jsonl"
    fpath.write_text("\n".join(json.dumps(r) for r in records))
    return fpath


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_cli_analyze_exits_zero(tmp_path: Path) -> None:
    """CLI 'analyze' subcommand exits 0 and writes an output file."""
    traces = _make_synthetic_traces(tmp_path)
    output_file = tmp_path / "stage_analysis.md"

    result = _run(
        "analyze",
        "--traces", str(traces),
        "--output", str(output_file),
    )

    assert result.returncode == 0, (
        f"CLI exited non-zero:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert output_file.exists(), f"Expected output file at {output_file}"


def test_cli_analyze_output_has_sections(tmp_path: Path) -> None:
    """CLI 'analyze' output Markdown contains required structural sections."""
    traces = _make_synthetic_traces(tmp_path)
    output_file = tmp_path / "stage_analysis.md"

    result = _run(
        "analyze",
        "--traces", str(traces),
        "--output", str(output_file),
    )
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

    content = output_file.read_text()
    for section in ["Summary", "Categories", "H1a", "H1b"]:
        assert section in content, (
            f"Expected section '{section}' in report, got:\n{content[:600]}"
        )


def test_cli_hypothesis_test_exits_zero(tmp_path: Path) -> None:
    """CLI 'hypothesis-test' subcommand exits 0 and writes a JSON verdicts file."""
    traces = _make_synthetic_traces(tmp_path)
    output_file = tmp_path / "verdicts.json"

    result = _run(
        "hypothesis-test",
        "--traces", str(traces),
        "--output", str(output_file),
    )

    assert result.returncode == 0, (
        f"CLI exited non-zero:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert output_file.exists(), f"Expected verdicts file at {output_file}"


def test_cli_hypothesis_test_json_structure(tmp_path: Path) -> None:
    """'hypothesis-test' output JSON has expected keys."""
    traces = _make_synthetic_traces(tmp_path)
    output_file = tmp_path / "verdicts.json"

    result = _run(
        "hypothesis-test",
        "--traces", str(traces),
        "--output", str(output_file),
    )
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

    with open(output_file) as f:
        data = json.load(f)

    for key in ("h1a_confirmed", "h1a_fraction", "h1b_confirmed", "h1b_fraction", "evidence"):
        assert key in data, f"Expected key '{key}' in verdicts JSON, got keys: {list(data.keys())}"


def test_cli_hypothesis_test_values_plausible(tmp_path: Path) -> None:
    """With 3 gsce + 2 gscs out of 7 empties → h1a_fraction should be ~0.714, h1a_confirmed=True."""
    traces = _make_synthetic_traces(tmp_path)
    output_file = tmp_path / "verdicts.json"

    result = _run(
        "hypothesis-test",
        "--traces", str(traces),
        "--output", str(output_file),
    )
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

    with open(output_file) as f:
        data = json.load(f)

    # 3 gsce + 2 gscs = 5 h1a-supporting out of 9 empties → 5/9 ≈ 0.556 ≥ 0.40 → confirmed
    assert data["h1a_confirmed"] is True, (
        f"Expected h1a_confirmed=True with this fixture, got h1a_fraction={data.get('h1a_fraction')}"
    )
    # h1b: 3 gsce out of 9 empties → 3/9 ≈ 0.333 < 0.40 → not confirmed
    assert data["h1b_confirmed"] is False, (
        f"Expected h1b_confirmed=False with this fixture, got h1b_fraction={data.get('h1b_fraction')}"
    )
