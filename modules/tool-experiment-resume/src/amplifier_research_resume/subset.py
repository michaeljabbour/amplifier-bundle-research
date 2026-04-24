"""
subset.py — Write items-to-rerun jsonl from a resume manifest.

Reads the full-input file and emits only the items that appear in
``errored_items ∪ never_started_items`` of the manifest.  The original item
structure is preserved exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

from .manifest import ResumeManifest


def write_subset(
    manifest: ResumeManifest,
    full_input: Path,
    output_jsonl: Path,
) -> int:
    """Write a jsonl containing only items that need re-running.

    Args:
        manifest: The :class:`ResumeManifest` produced by ``plan``.
        full_input: Path to the original full-input jsonl.  Each line must
            have an ``"id"`` (or ``"item_id"``) field.
        output_jsonl: Destination path.  Parent directories are created if
            needed.  File is overwritten if it exists.

    Returns:
        Number of items written.
    """
    full_input = Path(full_input)
    output_jsonl = Path(output_jsonl)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    # Build the set of item IDs to include
    rerun_ids = set(manifest.rerun_item_ids())

    written = 0
    with full_input.open(encoding="utf-8") as fin, output_jsonl.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            item_id = str(item.get("id") or item.get("item_id") or "")
            if item_id in rerun_ids:
                fout.write(json.dumps(item) + "\n")
                written += 1

    return written
