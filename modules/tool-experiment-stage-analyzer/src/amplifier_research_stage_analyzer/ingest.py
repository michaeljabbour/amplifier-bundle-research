"""
ingest.py — Load and validate stage_traces.jsonl.

Public API:
    ingest_stage_traces(path: str) -> list[dict]
"""

from __future__ import annotations

import json
from pathlib import Path

# Required top-level fields on every record.
_REQUIRED_TOP_FIELDS = (
    "item_id",
    "approach_id",
    "approach_name",
    "stages",
    "final_response_length",
    "final_is_empty",
    "timestamp",
)

# Required fields inside stages.generator (always present).
_REQUIRED_GENERATOR_FIELDS = (
    "output",
    "output_length",
    "latency_ms",
    "cost_usd",
    "is_empty",
    "is_truncated",
)


def _validate_record(record: dict, line_no: int) -> None:
    """Raise ValueError if *record* does not satisfy the stage-trace schema."""
    # --- Top-level required fields ---
    for field in _REQUIRED_TOP_FIELDS:
        if field not in record:
            raise ValueError(
                f"Line {line_no}: record missing required field '{field}'. "
                f"Keys present: {sorted(record.keys())}"
            )

    stages = record["stages"]
    if not isinstance(stages, dict):
        raise ValueError(f"Line {line_no}: 'stages' must be a dict, got {type(stages).__name__}")

    # --- generator stage is always required ---
    if stages.get("generator") is None:
        raise ValueError(
            f"Line {line_no}: stages.generator must be present (non-null) for every record. "
            f"item_id={record.get('item_id', '<unknown>')!r}"
        )

    generator = stages["generator"]
    if not isinstance(generator, dict):
        raise ValueError(
            f"Line {line_no}: stages.generator must be a dict, got {type(generator).__name__}"
        )

    for field in _REQUIRED_GENERATOR_FIELDS:
        if field not in generator:
            raise ValueError(
                f"Line {line_no}: stages.generator missing field '{field}'. "
                f"item_id={record.get('item_id', '<unknown>')!r}"
            )

    # critic and revert_decision are allowed to be None (A0-style records)


def ingest_stage_traces(path: str) -> list[dict]:
    """Load and validate a stage_traces.jsonl file.

    Args:
        path: Filesystem path to the ``.jsonl`` file.

    Returns:
        List of validated stage-trace records (one dict per line).

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If any line is not valid JSON or fails schema validation.

    Example:
        >>> records = ingest_stage_traces("experiments/foo/stage_traces.jsonl")
        >>> len(records)  # number of traces
        150
    """
    fpath = Path(path)
    if not fpath.exists():
        raise FileNotFoundError(f"stage_traces file not found: {path}")

    records: list[dict] = []
    raw_text = fpath.read_text(encoding="utf-8")

    for line_no, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue  # skip blank lines

        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Line {line_no}: invalid JSON — {exc}") from exc

        if not isinstance(record, dict):
            raise ValueError(f"Line {line_no}: expected a JSON object, got {type(record).__name__}")

        _validate_record(record, line_no)
        records.append(record)

    return records
