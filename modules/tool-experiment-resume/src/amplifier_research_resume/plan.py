"""
plan.py — Resume planning logic.

Reads a partial results file and a full-input jsonl, then categorises every
item into one of three buckets:

  - ``clean_complete``  — all approaches present, no [HANDLER_ERROR], no
    suspiciously-short responses.
  - ``errored``         — some approaches missing, or at least one record
    contains [HANDLER_ERROR], or a response is suspiciously short (1–9 chars).
  - ``never_started``   — item is in full_input but has zero records in
    the partial file.

Returns a :class:`~amplifier_research_resume.manifest.ResumeManifest`.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .manifest import ResumeManifest

# ---------------------------------------------------------------------------
# Error-detection helpers
# ---------------------------------------------------------------------------

_SHORT_RESPONSE_MIN = 1  # inclusive lower bound
_SHORT_RESPONSE_MAX = 10  # exclusive upper bound (< 10)


def _is_error_response(response: str) -> bool:
    """Return True if *response* indicates a pipeline failure.

    Rules:
    - Contains the literal string ``[HANDLER_ERROR]``.
    - Has a non-empty length that is suspiciously short (1 ≤ len < 10).
      Empty string ``""`` (len=0) is treated as a valid "no answer" response
      that the judge can still evaluate.
    """
    if "[HANDLER_ERROR]" in response:
        return True
    if _SHORT_RESPONSE_MIN <= len(response) < _SHORT_RESPONSE_MAX:
        return True
    return False


def _error_reason(r: dict) -> str:
    """Return a human-readable reason code for why a record is an error."""
    response = str(r.get("response") or "")
    if "[HANDLER_ERROR]" in response:
        return "HANDLER_ERROR"
    if _SHORT_RESPONSE_MIN <= len(response) < _SHORT_RESPONSE_MAX:
        return "SHORT_RESPONSE"
    return "MISSING_APPROACH"


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------


def _load_records(path: Path) -> list[dict]:
    """Load JSONL records from *path*, silently skipping malformed lines."""
    records: list[dict] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def _load_full_input_ids(path: Path) -> list[str]:
    """Load item IDs from a full-input jsonl.

    The full-input file uses ``"id"`` as the item identifier field (the
    original dataset schema), not ``"item_id"`` used by results files.
    """
    ids: list[str] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                item_id = obj.get("id") or obj.get("item_id")
                if item_id:
                    ids.append(str(item_id))
            except json.JSONDecodeError:
                pass
    return ids


def categorize_records(
    partial_results: Path,
    full_input: Path,
    approaches: list[str],
) -> ResumeManifest:
    """Categorise partial results and produce a :class:`ResumeManifest`.

    Args:
        partial_results: Path to the partial ``results.jsonl`` (or
            ``results.jsonl.partial``).
        full_input: Path to the original full-input jsonl whose ``id`` field
            lists every item that should have been run.
        approaches: List of approach IDs that were scheduled to run (e.g.
            ``["A0", "A4"]``).

    Returns:
        A :class:`ResumeManifest` with complete categorisation and totals.
    """
    partial_results = Path(partial_results)
    full_input = Path(full_input)

    # ------------------------------------------------------------------ #
    # Load data
    # ------------------------------------------------------------------ #
    records = _load_records(partial_results)
    full_ids = _load_full_input_ids(full_input)

    # Group partial records by item_id
    by_item: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in records:
        item_id = str(r.get("item_id", ""))
        approach_id = str(r.get("approach_id", ""))
        if item_id and approach_id:
            by_item[item_id][approach_id] = r

    partial_item_ids = set(by_item.keys())

    # ------------------------------------------------------------------ #
    # Categorise items present in partial
    # ------------------------------------------------------------------ #
    clean_complete: list[str] = []
    errored_items: list[dict] = []

    for item_id in partial_item_ids:
        item_approaches = by_item[item_id]
        item_errored = False
        errored_approach_names: list[str] = []
        reason: str = "UNKNOWN"

        for approach in approaches:
            if approach not in item_approaches:
                item_errored = True
                errored_approach_names.append(approach)
                reason = "MISSING_APPROACH"
                continue

            r = item_approaches[approach]
            response = str(r.get("response") or "")
            if _is_error_response(response):
                item_errored = True
                errored_approach_names.append(approach)
                reason = _error_reason(r)

        if item_errored:
            errored_items.append(
                {
                    "item_id": item_id,
                    "errored_approaches": errored_approach_names,
                    "reason": reason,
                }
            )
        else:
            clean_complete.append(item_id)

    # ------------------------------------------------------------------ #
    # Items in full_input but not in partial
    # ------------------------------------------------------------------ #
    never_started = [id_ for id_ in full_ids if id_ not in partial_item_ids]

    # ------------------------------------------------------------------ #
    # Totals
    # ------------------------------------------------------------------ #
    rerun_count = len(errored_items) + len(never_started)
    totals = {
        "clean_complete_count": len(clean_complete),
        "errored_count": len(errored_items),
        "never_started_count": len(never_started),
        "rerun_count": rerun_count,
        "expected_full_count": len(full_ids),
    }

    return ResumeManifest(
        version="1.0",
        source_partial=str(partial_results),
        source_full_input=str(full_input),
        approaches=approaches,
        categorization={
            "clean_complete_items": clean_complete,
            "errored_items": errored_items,
            "never_started_items": never_started,
        },
        totals=totals,
    )
