"""
TDD RED phase — test_ingest_robustness.py

Tests for null/missing stages.generator tolerance in ingest.py.
These must FAIL before the fix is implemented — the current code raises ValueError
unconditionally when stages.generator is null.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers (minimal copy of shared utilities — keeps this module self-contained)
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


def _make_record(
    item_id: str = "item_001",
    approach_id: str = "A1",
    approach_name: str = "Reflection",
    generator: dict | None = None,
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
            "critic": None,
            "revert_decision": None,
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


def test_ingest_drops_null_generator_records_with_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """5 records, 1 with null generator → returns 4 records and emits a WARNING."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = [_make_record(item_id=f"item_{i:03d}") for i in range(5)]
    # Null out the generator on the middle record
    records[2]["stages"]["generator"] = None

    fpath = _write_jsonl(tmp_path, records)

    with caplog.at_level(logging.WARNING, logger="amplifier_research_stage_analyzer.ingest"):
        result = ingest_stage_traces(str(fpath))  # must NOT raise

    assert len(result) == 4, f"Expected 4 records after dropping null-generator, got {len(result)}"
    returned_ids = [r["item_id"] for r in result]
    assert "item_002" not in returned_ids, "Null-generator record should have been dropped"
    assert any(
        "item_002" in msg or "null" in msg.lower() or "generator" in msg.lower()
        for msg in caplog.messages
    ), f"Expected a warning mentioning the dropped record; got messages: {caplog.messages}"


def test_ingest_dropped_count_in_metadata(tmp_path: Path) -> None:
    """Same 5-record/1-null fixture → result.dropped_count == 1 and item_id tracked."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = [_make_record(item_id=f"item_{i:03d}") for i in range(5)]
    records[2]["stages"]["generator"] = None

    fpath = _write_jsonl(tmp_path, records)

    result = ingest_stage_traces(str(fpath))

    assert hasattr(result, "dropped_count"), "IngestResult must expose .dropped_count"
    assert result.dropped_count == 1, f"Expected dropped_count=1, got {result.dropped_count}"

    assert hasattr(result, "dropped_item_ids"), "IngestResult must expose .dropped_item_ids"
    assert "item_002" in result.dropped_item_ids, (
        f"Expected 'item_002' in dropped_item_ids, got {result.dropped_item_ids}"
    )


def test_ingest_strict_mode_still_works_when_explicit(tmp_path: Path) -> None:
    """strict=True preserves the old ValueError-on-null-generator behaviour (backward compat)."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = [_make_record(item_id="bad_strict_001")]
    records[0]["stages"]["generator"] = None

    fpath = _write_jsonl(tmp_path, records)

    with pytest.raises(ValueError, match="generator"):
        ingest_stage_traces(str(fpath), strict=True)


def test_ingest_all_null_records_returns_empty_with_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """All 5 records have null generator → returns empty list, dropped_count=5, no crash."""
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = [_make_record(item_id=f"item_{i:03d}") for i in range(5)]
    for r in records:
        r["stages"]["generator"] = None

    fpath = _write_jsonl(tmp_path, records)

    with caplog.at_level(logging.WARNING, logger="amplifier_research_stage_analyzer.ingest"):
        result = ingest_stage_traces(str(fpath))  # must NOT raise

    assert len(result) == 0, f"Expected empty result, got {len(result)} records"
    assert result.dropped_count == 5, f"Expected dropped_count=5, got {result.dropped_count}"
    assert len(result.dropped_item_ids) == 5, (
        f"Expected 5 dropped_item_ids, got {result.dropped_item_ids}"
    )
    # Should have emitted one warning per dropped record
    assert len(caplog.messages) >= 5, (
        f"Expected at least 5 warning messages, got {len(caplog.messages)}: {caplog.messages}"
    )
