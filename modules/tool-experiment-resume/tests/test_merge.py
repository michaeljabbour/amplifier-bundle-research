"""
Tests for merge.py — TDD RED phase.

Covers:
  1. test_merge_combines_preserved_and_new
  2. test_merge_deduplicates_on_overlap
  3. test_merge_handles_missing_items_in_new_run
  4. test_merge_summary_reports_accurate_stats
"""

import json
from pathlib import Path

import pytest

from amplifier_research_resume.merge import merge_results, MergeSummary
from amplifier_research_resume.manifest import ResumeManifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "Long answer that is clearly meaningful and passes quality checks. " * 3


def _build_manifest(
    clean_items: list[str],
    errored_ids: list[str],
    never_started: list[str],
    approaches: list[str] = None,
) -> ResumeManifest:
    if approaches is None:
        approaches = ["A0", "A4"]
    rerun = errored_ids + never_started
    return ResumeManifest(
        version="1.0",
        source_partial="partial.jsonl",
        source_full_input="full_input.jsonl",
        approaches=approaches,
        categorization={
            "clean_complete_items": clean_items,
            "errored_items": [{"item_id": i, "errored_approaches": [], "reason": "HE"} for i in errored_ids],
            "never_started_items": never_started,
        },
        totals={
            "clean_complete_count": len(clean_items),
            "errored_count": len(errored_ids),
            "never_started_count": len(never_started),
            "rerun_count": len(rerun),
            "expected_full_count": len(clean_items) + len(rerun),
        },
    )


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _make_records(item_ids: list[str], approaches: list[str], response_prefix: str = "") -> list[dict]:
    records = []
    for item_id in item_ids:
        for approach in approaches:
            records.append({
                "item_id": item_id,
                "approach_id": approach,
                "response": f"{response_prefix}{LONG_RESPONSE}",
                "correct_by_judge": True,
            })
    return records


# ---------------------------------------------------------------------------
# Test 1: combines preserved + new
# ---------------------------------------------------------------------------


class TestMergeCombinesPreservedAndNew:
    def test_merge_combines_preserved_and_new(self, tmp_path):
        """Preserved has 244 records, new has 358; merged has 602 (no overlap)."""
        approaches = ["A0", "A4"]
        clean_ids = [f"clean_{i}" for i in range(122)]  # 122 × 2 = 244 records
        errored_ids = [f"err_{i}" for i in range(32)]
        never_started_ids = [f"new_{i}" for i in range(146)]  # 146 + 32 = 178 rerun
        rerun_ids = errored_ids + never_started_ids  # 178 items × 2 = 356 possible

        # New run completed all 178 rerun items (356 records) + one leftover
        new_records = _make_records(rerun_ids, approaches)  # 356 records

        partial_records = _make_records(clean_ids + errored_ids, approaches)  # 308 records

        partial_path = tmp_path / "partial.jsonl"
        new_results_path = tmp_path / "new_results.jsonl"
        _write_jsonl(partial_path, partial_records)
        _write_jsonl(new_results_path, new_records)

        manifest = _build_manifest(clean_ids, errored_ids, never_started_ids, approaches)

        output_path = tmp_path / "merged.jsonl"
        summary = merge_results(
            manifest=manifest,
            partial_results=partial_path,
            new_results=new_results_path,
            output_merged=output_path,
        )

        assert output_path.exists()
        merged_records = [json.loads(l) for l in output_path.read_text().splitlines() if l.strip()]
        # Preserved: 122 × 2 = 244; New: 178 × 2 = 356; Total: 600
        assert len(merged_records) == 244 + 356
        assert summary.preserved_count == 244
        assert summary.new_count == 356


# ---------------------------------------------------------------------------
# Test 2: deduplicates on overlap
# ---------------------------------------------------------------------------


class TestMergeDeduplicates:
    def test_merge_deduplicates_on_overlap(self, tmp_path):
        """Same (item_id, approach_id) in both → kept exactly once; new run wins."""
        approaches = ["A0", "A4"]
        clean_ids = ["clean_0", "clean_1"]
        errored_ids = ["err_0"]

        # Partial has both clean and errored
        partial_records = _make_records(clean_ids + errored_ids, approaches, response_prefix="OLD_")

        # New run has the errored item AND also (accidentally) a clean item
        new_records = _make_records(errored_ids + [clean_ids[0]], approaches, response_prefix="NEW_")

        partial_path = tmp_path / "partial.jsonl"
        new_results_path = tmp_path / "new_results.jsonl"
        _write_jsonl(partial_path, partial_records)
        _write_jsonl(new_results_path, new_records)

        manifest = _build_manifest(clean_ids, errored_ids, never_started=[])

        output_path = tmp_path / "merged.jsonl"
        summary = merge_results(
            manifest=manifest,
            partial_results=partial_path,
            new_results=new_results_path,
            output_merged=output_path,
        )

        merged_records = [json.loads(l) for l in output_path.read_text().splitlines() if l.strip()]
        # (clean_0 × 2) + (clean_1 × 2) + (err_0 × 2) = 6 unique, no duplication
        assert len(merged_records) == 6

        # New run should win for the overlapping item (clean_0, A0/A4)
        clean_0_records = [r for r in merged_records if r["item_id"] == "clean_0"]
        assert all("NEW_" in r["response"] for r in clean_0_records)


# ---------------------------------------------------------------------------
# Test 3: handles missing items in new run
# ---------------------------------------------------------------------------


class TestMergeHandlesMissingInNewRun:
    def test_merge_handles_missing_items_in_new_run(self, tmp_path):
        """New run only completed 100 of 178 attempted → summary flags the gap."""
        approaches = ["A0", "A4"]
        clean_ids = [f"clean_{i}" for i in range(122)]
        errored_ids = [f"err_{i}" for i in range(32)]
        never_started_ids = [f"new_{i}" for i in range(146)]
        rerun_ids = errored_ids + never_started_ids  # 178

        # New run only completed 100 of 178 rerun items
        completed_rerun = rerun_ids[:100]
        partial_records = _make_records(clean_ids + errored_ids, approaches)
        new_records = _make_records(completed_rerun, approaches)  # 100 × 2 = 200

        partial_path = tmp_path / "partial.jsonl"
        new_results_path = tmp_path / "new_results.jsonl"
        _write_jsonl(partial_path, partial_records)
        _write_jsonl(new_results_path, new_records)

        manifest = _build_manifest(clean_ids, errored_ids, never_started_ids, approaches)

        output_path = tmp_path / "merged.jsonl"
        summary = merge_results(
            manifest=manifest,
            partial_results=partial_path,
            new_results=new_results_path,
            output_merged=output_path,
        )

        # 244 preserved + 200 new = 444 total records
        merged_records = [json.loads(l) for l in output_path.read_text().splitlines() if l.strip()]
        assert len(merged_records) == 244 + 200

        # Summary should flag missing items
        assert summary.has_gap
        assert summary.expected_items == 300
        assert len(summary.missing_items) == 78  # 178 - 100 = 78 items not completed


# ---------------------------------------------------------------------------
# Test 4: summary reports accurate stats
# ---------------------------------------------------------------------------


class TestMergeSummaryStats:
    def test_merge_summary_reports_accurate_stats(self, tmp_path):
        """Verify all count fields in summary output are accurate."""
        approaches = ["A0", "A4"]
        clean_ids = [f"c_{i}" for i in range(5)]
        errored_ids = [f"e_{i}" for i in range(3)]
        never_started_ids = [f"n_{i}" for i in range(2)]

        partial_records = _make_records(clean_ids + errored_ids, approaches)
        new_records = _make_records(errored_ids + never_started_ids, approaches)

        partial_path = tmp_path / "partial.jsonl"
        new_results_path = tmp_path / "new_results.jsonl"
        _write_jsonl(partial_path, partial_records)
        _write_jsonl(new_results_path, new_records)

        manifest = _build_manifest(clean_ids, errored_ids, never_started_ids, approaches)

        output_path = tmp_path / "merged.jsonl"
        summary = merge_results(
            manifest=manifest,
            partial_results=partial_path,
            new_results=new_results_path,
            output_merged=output_path,
        )

        # Preserved = clean_ids × 2 approaches
        assert summary.preserved_count == len(clean_ids) * len(approaches)
        # New = (errored + never_started) × 2 approaches
        assert summary.new_count == (len(errored_ids) + len(never_started_ids)) * len(approaches)
        # Total merged = preserved + new
        assert summary.merged_total == summary.preserved_count + summary.new_count
        # Expected = all items × 2 approaches
        assert summary.expected_records == (len(clean_ids) + len(errored_ids) + len(never_started_ids)) * len(approaches)
        # No gap when all rerun items completed
        assert not summary.has_gap
        assert summary.missing_items == []
