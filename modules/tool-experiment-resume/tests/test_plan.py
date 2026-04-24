"""
Tests for plan.py — TDD RED phase.

Covers:
  1. test_plan_categorizes_clean_complete_items
  2. test_plan_categorizes_handler_error_as_errored
  3. test_plan_categorizes_missing_approach_as_errored
  4. test_plan_identifies_never_started
  5. test_plan_short_response_treated_as_error
  6. test_plan_serialization_roundtrip
"""

import json
from pathlib import Path

import pytest

from amplifier_research_resume.plan import categorize_records
from amplifier_research_resume.manifest import ResumeManifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "This is a sufficiently long response that passes length checks. " * 3


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _write_full_input(path: Path, item_ids: list[str]) -> None:
    """Write a minimal full-input jsonl with `id` field per item."""
    with path.open("w") as f:
        for item_id in item_ids:
            f.write(json.dumps({"id": item_id, "question": f"Q for {item_id}"}) + "\n")


def _make_clean_records(item_ids: list[str], approaches: list[str]) -> list[dict]:
    """Make clean records for all items × approaches."""
    records = []
    for item_id in item_ids:
        for approach in approaches:
            records.append({
                "item_id": item_id,
                "approach_id": approach,
                "response": LONG_RESPONSE,
                "correct_by_judge": True,
            })
    return records


# ---------------------------------------------------------------------------
# Test 1: categorizes clean complete items
# ---------------------------------------------------------------------------


class TestCategorizeCleanComplete:
    def test_plan_categorizes_clean_complete_items(self, tmp_path):
        """5 items × 2 approaches, all clean → 5 items in clean_complete_items."""
        item_ids = [f"item_{i}" for i in range(5)]
        approaches = ["A0", "A4"]

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"

        _write_jsonl(partial_path, _make_clean_records(item_ids, approaches))
        _write_full_input(full_input_path, item_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        assert set(manifest.categorization["clean_complete_items"]) == set(item_ids)
        assert manifest.categorization["errored_items"] == []
        assert manifest.categorization["never_started_items"] == []
        assert manifest.totals["clean_complete_count"] == 5
        assert manifest.totals["errored_count"] == 0
        assert manifest.totals["never_started_count"] == 0


# ---------------------------------------------------------------------------
# Test 2: HANDLER_ERROR → errored
# ---------------------------------------------------------------------------


class TestHandlerError:
    def test_plan_categorizes_handler_error_as_errored(self, tmp_path):
        """A4 has [HANDLER_ERROR] for item_3 → item_3 in errored, others clean."""
        item_ids = [f"item_{i}" for i in range(5)]
        approaches = ["A0", "A4"]

        records = _make_clean_records(item_ids, approaches)
        # Corrupt item_3's A4 response
        for r in records:
            if r["item_id"] == "item_3" and r["approach_id"] == "A4":
                r["response"] = "[HANDLER_ERROR] provider overloaded"

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        _write_jsonl(partial_path, records)
        _write_full_input(full_input_path, item_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        clean = set(manifest.categorization["clean_complete_items"])
        errored_ids = [e["item_id"] for e in manifest.categorization["errored_items"]]

        assert "item_3" in errored_ids
        assert "item_3" not in clean
        # Other items remain clean
        for item_id in item_ids:
            if item_id != "item_3":
                assert item_id in clean
        assert manifest.totals["errored_count"] == 1


# ---------------------------------------------------------------------------
# Test 3: missing approach → errored
# ---------------------------------------------------------------------------


class TestMissingApproach:
    def test_plan_categorizes_missing_approach_as_errored(self, tmp_path):
        """item_2 has only A0 record (no A4) → item_2 in errored."""
        item_ids = [f"item_{i}" for i in range(5)]
        approaches = ["A0", "A4"]

        # Only give item_2 the A0 record; omit its A4 record
        records = []
        for item_id in item_ids:
            for approach in approaches:
                if item_id == "item_2" and approach == "A4":
                    continue  # skip A4 for item_2
                records.append({
                    "item_id": item_id,
                    "approach_id": approach,
                    "response": LONG_RESPONSE,
                    "correct_by_judge": True,
                })

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        _write_jsonl(partial_path, records)
        _write_full_input(full_input_path, item_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        errored_ids = [e["item_id"] for e in manifest.categorization["errored_items"]]
        clean = set(manifest.categorization["clean_complete_items"])

        assert "item_2" in errored_ids
        assert "item_2" not in clean

        # Check that the errored entry records which approach is missing
        item_2_errored = next(e for e in manifest.categorization["errored_items"] if e["item_id"] == "item_2")
        assert "A4" in item_2_errored.get("errored_approaches", [])


# ---------------------------------------------------------------------------
# Test 4: never_started items
# ---------------------------------------------------------------------------


class TestNeverStarted:
    def test_plan_identifies_never_started(self, tmp_path):
        """Full input has 10 items, partial has records for only 6 → 4 in never_started."""
        all_ids = [f"item_{i}" for i in range(10)]
        started_ids = all_ids[:6]
        approaches = ["A0", "A4"]

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        _write_jsonl(partial_path, _make_clean_records(started_ids, approaches))
        _write_full_input(full_input_path, all_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        never_started = set(manifest.categorization["never_started_items"])
        expected_never = set(all_ids[6:])

        assert never_started == expected_never
        assert manifest.totals["never_started_count"] == 4
        assert manifest.totals["rerun_count"] == 4  # all never_started, no errored


# ---------------------------------------------------------------------------
# Test 5: short response treated as error
# ---------------------------------------------------------------------------


class TestShortResponse:
    def test_plan_short_response_treated_as_error(self, tmp_path):
        """Item with response of length 1-9 chars → errored (suspiciously short)."""
        item_ids = [f"item_{i}" for i in range(3)]
        approaches = ["A0", "A4"]

        records = _make_clean_records(item_ids, approaches)
        # Give item_1's A4 a suspiciously short (non-empty) response
        for r in records:
            if r["item_id"] == "item_1" and r["approach_id"] == "A4":
                r["response"] = "yes"  # 3 chars — suspiciously short

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        _write_jsonl(partial_path, records)
        _write_full_input(full_input_path, item_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        errored_ids = [e["item_id"] for e in manifest.categorization["errored_items"]]
        assert "item_1" in errored_ids

        # Other items remain clean
        clean = set(manifest.categorization["clean_complete_items"])
        assert "item_0" in clean
        assert "item_2" in clean


# ---------------------------------------------------------------------------
# Test 6: serialization roundtrip
# ---------------------------------------------------------------------------


class TestSerializationRoundtrip:
    def test_plan_serialization_roundtrip(self, tmp_path):
        """Write manifest to JSON and reload — equality holds."""
        item_ids = [f"item_{i}" for i in range(4)]
        approaches = ["A0", "A4"]

        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        _write_jsonl(partial_path, _make_clean_records(item_ids, approaches))
        _write_full_input(full_input_path, item_ids)

        manifest = categorize_records(
            partial_results=partial_path,
            full_input=full_input_path,
            approaches=approaches,
        )

        manifest_path = tmp_path / "manifest.json"
        manifest.save(manifest_path)

        loaded = ResumeManifest.load(manifest_path)

        assert loaded.version == manifest.version
        assert set(loaded.categorization["clean_complete_items"]) == set(
            manifest.categorization["clean_complete_items"]
        )
        assert loaded.totals == manifest.totals
        assert loaded.approaches == manifest.approaches
