"""
ingest.py — Load and validate stage_traces.jsonl.

Public API:
    ingest_stage_traces(path: str, strict: bool = False) -> IngestResult
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

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


class IngestResult(list):
    """A ``list`` of validated stage-trace records with dropped-record metadata.

    Behaves exactly like a plain ``list[dict]`` for all iteration and indexing,
    but exposes two extra attributes:

    Attributes:
        dropped_count: Number of records skipped due to incomplete stage data
            (null ``stages.generator``).
        dropped_item_ids: List of ``item_id`` strings for each dropped record,
            in the order they were encountered.
    """

    def __init__(
        self,
        records: list[dict],
        dropped_count: int = 0,
        dropped_item_ids: list[str] | None = None,
    ) -> None:
        super().__init__(records)
        self.dropped_count: int = dropped_count
        self.dropped_item_ids: list[str] = dropped_item_ids if dropped_item_ids is not None else []


def _validate_record(record: dict, line_no: int) -> None:
    """Raise ValueError if *record* does not satisfy the stage-trace schema.

    Note: null ``stages.generator`` is handled upstream in ``ingest_stage_traces``
    before this function is called, so by the time we reach here the generator
    is guaranteed to be a non-null dict.
    """
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

    generator = stages.get("generator")
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


def ingest_stage_traces(path: str, strict: bool = False) -> IngestResult:
    """Load and validate a stage_traces.jsonl file.

    Args:
        path: Filesystem path to the ``.jsonl`` file.
        strict: When ``True``, raises ``ValueError`` on the first record where
            ``stages.generator`` is null (legacy behaviour, useful for callers
            that require every record to be complete).  When ``False`` (default),
            records with a null ``stages.generator`` are skipped with a WARNING
            log message and tracked in the returned :class:`IngestResult`.

    Returns:
        :class:`IngestResult` — a ``list`` of validated stage-trace records.
        Access ``.dropped_count`` and ``.dropped_item_ids`` on the return value
        to inspect records that were dropped due to incomplete stage data.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If any line is not valid JSON, fails top-level schema
            validation, or (when ``strict=True``) has a null generator.

    Example:
        >>> result = ingest_stage_traces("experiments/foo/stage_traces.jsonl")
        >>> len(result)  # number of accepted traces
        150
        >>> result.dropped_count  # incomplete records skipped
        1
    """
    fpath = Path(path)
    if not fpath.exists():
        raise FileNotFoundError(f"stage_traces file not found: {path}")

    records: list[dict] = []
    dropped_item_ids: list[str] = []
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

        # --- Handle null stages.generator before full validation ---
        stages = record.get("stages")
        if isinstance(stages, dict) and stages.get("generator") is None:
            if strict:
                raise ValueError(
                    f"Line {line_no}: stages.generator must be present (non-null). "
                    f"item_id={record.get('item_id', '<unknown>')!r}"
                )
            item_id = str(record.get("item_id", "<unknown>"))
            _logger.warning(
                "Line %d: dropping record with null stages.generator — treating as incomplete "
                "(item_id=%r). Pass strict=True to raise instead.",
                line_no,
                item_id,
            )
            dropped_item_ids.append(item_id)
            continue

        _validate_record(record, line_no)
        records.append(record)

    return IngestResult(
        records,
        dropped_count=len(dropped_item_ids),
        dropped_item_ids=dropped_item_ids,
    )
