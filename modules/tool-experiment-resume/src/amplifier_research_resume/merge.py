"""
merge.py — Combine preserved records + new run results into a unified file.

Logic:
  1. Load preserved records: filter partial results to items in
     ``clean_complete_items``.
  2. Load new records from the new results file.
  3. Concatenate.
  4. Deduplicate by (item_id, approach_id) — new run wins on collision.
  5. Write merged jsonl.
  6. Return a :class:`MergeSummary` describing the outcome.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import ResumeManifest

# ---------------------------------------------------------------------------
# Summary dataclass
# ---------------------------------------------------------------------------


@dataclass
class MergeSummary:
    """Statistics and gap-detection result from a merge operation.

    Attributes:
        preserved_count: Number of records kept from the original partial file.
        new_count: Number of records added from the new run.
        merged_total: Total records written to the merged file.
        expected_records: Expected total (expected_full_count × n_approaches).
        expected_items: Expected number of distinct items (expected_full_count).
        merged_items: Number of distinct items in the merged file.
        missing_items: Item IDs that are absent from the merged file when
            compared against the full expected set.
        has_gap: True when ``merged_items < expected_items``.
    """

    preserved_count: int
    new_count: int
    merged_total: int
    expected_records: int
    expected_items: int
    merged_items: int
    missing_items: list[str] = field(default_factory=list)

    @property
    def has_gap(self) -> bool:
        return self.merged_items < self.expected_items

    def format_report(self) -> str:
        """Return a human-readable summary string."""
        lines = [
            "Merge summary:",
            f"  Preserved records: {self.preserved_count}",
            f"  New records:       {self.new_count}",
            f"  Merged total:      {self.merged_total}",
            f"  Items in merged:   {self.merged_items}",
            f"  Expected:          {self.expected_items}",
        ]
        if self.has_gap:
            lines.append(f"  Missing items ({len(self.missing_items)}): {self.missing_items[:10]}")
            if len(self.missing_items) > 10:
                lines.append(f"    ... and {len(self.missing_items) - 10} more")
        else:
            lines.append("  No gap — all expected items present.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> list[dict]:
    """Load records from a jsonl file, skipping blank/malformed lines."""
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


def merge_results(
    manifest: ResumeManifest,
    partial_results: Path,
    new_results: Path,
    output_merged: Path,
) -> MergeSummary:
    """Merge preserved records with new run results.

    Args:
        manifest: The :class:`ResumeManifest` that describes the resume plan.
        partial_results: Path to the original partial results file (source of
            preserved records).
        new_results: Path to the ``results.jsonl`` from the resume run.
        output_merged: Destination path for the unified merged file.

    Returns:
        A :class:`MergeSummary` with counts and gap information.
    """
    partial_results = Path(partial_results)
    new_results = Path(new_results)
    output_merged = Path(output_merged)
    output_merged.parent.mkdir(parents=True, exist_ok=True)

    clean_ids = set(manifest.categorization.get("clean_complete_items", []))

    # ------------------------------------------------------------------ #
    # 1. Load preserved records (clean_complete_items only)
    # ------------------------------------------------------------------ #
    partial_records = _load_jsonl(partial_results)
    preserved = [r for r in partial_records if str(r.get("item_id", "")) in clean_ids]

    # ------------------------------------------------------------------ #
    # 2. Load new records
    # ------------------------------------------------------------------ #
    new_records = _load_jsonl(new_results)

    # ------------------------------------------------------------------ #
    # 3. Deduplicate: new run wins on (item_id, approach_id) collision
    # ------------------------------------------------------------------ #
    # Seed with preserved records, then overwrite with new
    merged_map: dict[tuple[str, str], dict] = {}
    for r in preserved:
        key = (str(r.get("item_id", "")), str(r.get("approach_id", "")))
        merged_map[key] = r
    for r in new_records:
        key = (str(r.get("item_id", "")), str(r.get("approach_id", "")))
        merged_map[key] = r  # new run overwrites

    merged = list(merged_map.values())

    # ------------------------------------------------------------------ #
    # 4. Write merged file
    # ------------------------------------------------------------------ #
    with output_merged.open("w", encoding="utf-8") as fout:
        for r in merged:
            fout.write(json.dumps(r) + "\n")

    # ------------------------------------------------------------------ #
    # 5. Compute summary
    # ------------------------------------------------------------------ #
    merged_item_ids = {str(r.get("item_id", "")) for r in merged}
    expected_items = manifest.totals.get("expected_full_count", 0)
    expected_records = expected_items * len(manifest.approaches)

    # All expected item IDs: clean + errored + never_started
    all_expected_ids = set(
        manifest.categorization.get("clean_complete_items", [])
        + [e["item_id"] for e in manifest.categorization.get("errored_items", [])]
        + manifest.categorization.get("never_started_items", [])
    )
    missing_items = sorted(all_expected_ids - merged_item_ids)

    return MergeSummary(
        preserved_count=len(preserved),
        new_count=len(new_records),
        merged_total=len(merged),
        expected_records=expected_records,
        expected_items=expected_items,
        merged_items=len(merged_item_ids),
        missing_items=missing_items,
    )
