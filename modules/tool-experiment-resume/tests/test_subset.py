"""
Tests for subset.py — TDD RED phase.

Covers:
  1. test_subset_writes_only_rerun_items
  2. test_subset_preserves_item_structure
  3. test_subset_handles_empty_rerun_list
"""

import json
from pathlib import Path

import pytest

from amplifier_research_resume.subset import write_subset
from amplifier_research_resume.manifest import ResumeManifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "Long response that passes all quality checks. " * 4


def _build_manifest(
    clean_items: list[str],
    errored_items: list[str],
    never_started: list[str],
    approaches: list[str] = None,
    source_partial: str = "partial.jsonl",
    source_full_input: str = "full_input.jsonl",
) -> ResumeManifest:
    """Build a ResumeManifest directly for testing subset logic."""
    if approaches is None:
        approaches = ["A0", "A4"]
    rerun_count = len(errored_items) + len(never_started)
    return ResumeManifest(
        version="1.0",
        source_partial=source_partial,
        source_full_input=source_full_input,
        approaches=approaches,
        categorization={
            "clean_complete_items": clean_items,
            "errored_items": [{"item_id": i, "errored_approaches": [], "reason": "HANDLER_ERROR"} for i in errored_items],
            "never_started_items": never_started,
        },
        totals={
            "clean_complete_count": len(clean_items),
            "errored_count": len(errored_items),
            "never_started_count": len(never_started),
            "rerun_count": rerun_count,
            "expected_full_count": len(clean_items) + rerun_count,
        },
    )


def _write_full_input(path: Path, items: list[dict]) -> None:
    with path.open("w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


# ---------------------------------------------------------------------------
# Test 1: writes only rerun items
# ---------------------------------------------------------------------------


class TestSubsetWritesOnlyRerunItems:
    def test_subset_writes_only_rerun_items(self, tmp_path):
        """Manifest with 5 errored + 3 never_started → 8 items in output jsonl."""
        clean_ids = [f"clean_{i}" for i in range(7)]
        errored_ids = [f"errored_{i}" for i in range(5)]
        never_started_ids = [f"new_{i}" for i in range(3)]

        all_ids = clean_ids + errored_ids + never_started_ids
        full_items = [{"id": id_, "question": f"Q for {id_}"} for id_ in all_ids]

        full_input_path = tmp_path / "full_input.jsonl"
        _write_full_input(full_input_path, full_items)

        manifest = _build_manifest(clean_ids, errored_ids, never_started_ids)
        output_path = tmp_path / "rerun.jsonl"

        write_subset(manifest=manifest, full_input=full_input_path, output_jsonl=output_path)

        assert output_path.exists()
        output_records = [json.loads(line) for line in output_path.read_text().splitlines() if line.strip()]
        output_ids = {r["id"] for r in output_records}

        expected_ids = set(errored_ids) | set(never_started_ids)
        assert output_ids == expected_ids
        assert len(output_records) == 8


# ---------------------------------------------------------------------------
# Test 2: preserves item structure
# ---------------------------------------------------------------------------


class TestSubsetPreservesItemStructure:
    def test_subset_preserves_item_structure(self, tmp_path):
        """Items with extra fields (metadata, tags) — all fields preserved in output."""
        rerun_ids = ["item_A", "item_B"]
        items = [
            {
                "id": "item_A",
                "question": "What is X?",
                "answer": "42",
                "metadata": {"source": "dataset_v1"},
                "tags": ["science", "math"],
            },
            {
                "id": "item_B",
                "question": "What is Y?",
                "answer": "100",
                "metadata": {"source": "dataset_v2"},
                "tags": ["history"],
            },
            {
                "id": "clean_1",
                "question": "Clean item",
                "answer": "X",
            },
        ]

        full_input_path = tmp_path / "full_input.jsonl"
        _write_full_input(full_input_path, items)

        manifest = _build_manifest(clean_items=["clean_1"], errored_items=[], never_started=rerun_ids)
        output_path = tmp_path / "rerun.jsonl"

        write_subset(manifest=manifest, full_input=full_input_path, output_jsonl=output_path)

        output_records = {r["id"]: r for r in [json.loads(l) for l in output_path.read_text().splitlines() if l.strip()]}

        assert output_records["item_A"]["metadata"] == {"source": "dataset_v1"}
        assert output_records["item_A"]["tags"] == ["science", "math"]
        assert output_records["item_B"]["metadata"] == {"source": "dataset_v2"}


# ---------------------------------------------------------------------------
# Test 3: handles empty rerun list
# ---------------------------------------------------------------------------


class TestSubsetEmptyRerunList:
    def test_subset_handles_empty_rerun_list(self, tmp_path):
        """Manifest says 0 rerun → output file is created and empty (no records)."""
        clean_ids = ["item_1", "item_2", "item_3"]
        full_items = [{"id": id_, "question": f"Q for {id_}"} for id_ in clean_ids]

        full_input_path = tmp_path / "full_input.jsonl"
        _write_full_input(full_input_path, full_items)

        manifest = _build_manifest(clean_items=clean_ids, errored_items=[], never_started=[])
        output_path = tmp_path / "rerun.jsonl"

        write_subset(manifest=manifest, full_input=full_input_path, output_jsonl=output_path)

        assert output_path.exists()
        content = output_path.read_text().strip()
        # Either empty file or file with no records
        if content:
            records = [json.loads(l) for l in content.splitlines() if l.strip()]
            assert len(records) == 0
