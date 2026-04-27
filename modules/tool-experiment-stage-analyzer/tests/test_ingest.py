"""
TDD RED phase — test_ingest.py

Tests for ingest.py: load and validate stage_traces.jsonl.
These tests import from amplifier_research_stage_analyzer.ingest,
which does NOT exist yet.  All tests must FAIL on first run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_generator_stage(
    output: str = "x" * 200,
    output_length: int = 200,
    is_empty: bool = False,
    is_truncated: bool = False,
    latency_ms: float = 1000.0,
    cost_usd: float = 0.001,
) -> dict:
    return {
        "output": output,
        "output_length": output_length,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "is_empty": is_empty,
        "is_truncated": is_truncated,
    }


def _make_critic_stage(
    output: str = "y" * 150,
    output_length: int = 150,
    is_empty: bool = False,
    verdict: str = "keep",
    latency_ms: float = 800.0,
    cost_usd: float = 0.0008,
) -> dict:
    return {
        "output": output,
        "output_length": output_length,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "is_empty": is_empty,
        "verdict": verdict,
    }


def _make_record(
    item_id: str = "item_001",
    approach_id: str = "A1",
    approach_name: str = "Reflection",
    generator: dict | None = None,
    critic: dict | None = None,
    revert_decision: dict | None = None,
    final_response_length: int = 200,
    final_is_empty: bool = False,
    timestamp: str = "2024-01-01T00:00:00Z",
) -> dict:
    return {
        "item_id": item_id,
        "approach_id": approach_id,
        "approach_name": approach_name,
        "stages": {
            "generator": generator if generator is not None else _make_generator_stage(),
            "critic": critic,
            "revert_decision": revert_decision,
        },
        "final_response_length": final_response_length,
        "final_is_empty": final_is_empty,
        "timestamp": timestamp,
    }


def _write_jsonl(tmp_path: Path, records: list[dict]) -> Path:
    fpath = tmp_path / "stage_traces.jsonl"
    fpath.write_text("\n".join(json.dumps(r) for r in records))
    return fpath


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_ingest_valid_traces(tmp_path: Path) -> None:
    """Five valid records are ingested and returned as a list of 5."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = [_make_record(item_id=f"item_{i:03d}", approach_id="A1") for i in range(5)]
    fpath = _write_jsonl(tmp_path, records)

    result = ingest_stage_traces(str(fpath))

    assert isinstance(result, list), "Expected a list of records"
    assert len(result) == 5, f"Expected 5 records, got {len(result)}"
    assert result[0]["item_id"] == "item_000"
    assert result[4]["item_id"] == "item_004"


def test_ingest_rejects_malformed_jsonl(tmp_path: Path) -> None:
    """Records missing required 'item_id' raise ValueError with a clear message."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    bad_record = {
        # "item_id" is intentionally missing
        "approach_id": "A1",
        "approach_name": "Reflection",
        "stages": {
            "generator": _make_generator_stage(),
            "critic": None,
            "revert_decision": None,
        },
        "final_response_length": 200,
        "final_is_empty": False,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    fpath = _write_jsonl(tmp_path, [bad_record])

    with pytest.raises(ValueError, match="item_id"):
        ingest_stage_traces(str(fpath))


def test_ingest_handles_null_stages_for_a0(tmp_path: Path) -> None:
    """A0-style records with critic=null and revert_decision=null are ingested cleanly."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    a0_record = _make_record(
        item_id="a0_item_001",
        approach_id="A0",
        approach_name="Baseline",
        critic=None,
        revert_decision=None,
        final_response_length=200,
        final_is_empty=False,
    )
    fpath = _write_jsonl(tmp_path, [a0_record])

    result = ingest_stage_traces(str(fpath))

    assert len(result) == 1
    assert result[0]["item_id"] == "a0_item_001"
    assert result[0]["stages"]["critic"] is None
    assert result[0]["stages"]["revert_decision"] is None


def test_ingest_rejects_missing_generator(tmp_path: Path) -> None:
    """In strict mode, stages.generator=null raises ValueError (backward-compat)."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    bad_record = _make_record(item_id="bad_001")
    bad_record["stages"]["generator"] = None  # type: ignore[assignment]
    fpath = _write_jsonl(tmp_path, [bad_record])

    with pytest.raises(ValueError, match="generator"):
        ingest_stage_traces(str(fpath), strict=True)


def test_ingest_rejects_invalid_json_lines(tmp_path: Path) -> None:
    """Lines that are not valid JSON raise ValueError."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    fpath = tmp_path / "stage_traces.jsonl"
    good_line = json.dumps(_make_record(item_id="ok_001"))
    fpath.write_text(good_line + "\nTHIS IS NOT JSON\n")

    with pytest.raises(ValueError):
        ingest_stage_traces(str(fpath))
