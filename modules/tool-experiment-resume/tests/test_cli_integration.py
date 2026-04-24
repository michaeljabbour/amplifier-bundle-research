"""
End-to-end integration test for the CLI: plan → subset → (mock new run) → merge.

Covers:
  1. Full pipeline: partial → manifest → subset → (mock rerun) → merged
"""

import json
import sys
from pathlib import Path

import pytest

from amplifier_research_resume.cli import main as cli_main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESPONSE = "This is a valid and substantive response to the question. " * 5


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _make_partial(
    item_ids: list[str],
    approaches: list[str],
    error_item_id: str | None = None,
    error_approach: str | None = None,
) -> list[dict]:
    """Create partial results with optional single error record."""
    records = []
    for item_id in item_ids:
        for approach in approaches:
            is_error = (item_id == error_item_id and approach == error_approach)
            records.append({
                "item_id": item_id,
                "approach_id": approach,
                "response": "[HANDLER_ERROR]" if is_error else LONG_RESPONSE,
                "correct_by_judge": None if is_error else True,
            })
    return records


# ---------------------------------------------------------------------------
# End-to-end test
# ---------------------------------------------------------------------------


class TestCliEndToEnd:
    def test_plan_subset_mock_merge_pipeline(self, tmp_path, monkeypatch):
        """
        Full pipeline:
          1. plan: classify partial results → manifest
          2. subset: write items to rerun → rerun.jsonl
          3. (mock) simulate new run for rerun items
          4. merge: combine preserved + new → merged.jsonl
          5. Verify final state
        """
        approaches = ["A0", "A4"]
        # 6 items started, 1 with HANDLER_ERROR, 4 never started
        started_ids = [f"item_{i}" for i in range(6)]
        never_started_ids = [f"new_{i}" for i in range(4)]
        all_ids = started_ids + never_started_ids  # 10 total

        partial_records = _make_partial(
            started_ids, approaches,
            error_item_id="item_0", error_approach="A4",
        )

        # Write files
        partial_path = tmp_path / "results.jsonl.partial"
        full_input_path = tmp_path / "full_input.jsonl"
        manifest_path = tmp_path / "resume_manifest.json"
        rerun_path = tmp_path / "rerun.jsonl"
        new_results_path = tmp_path / "new_results.jsonl"
        merged_path = tmp_path / "merged.jsonl"

        _write_jsonl(partial_path, partial_records)
        # Write full input (item_id field = "id")
        with full_input_path.open("w") as f:
            for id_ in all_ids:
                f.write(json.dumps({"id": id_, "question": f"Q for {id_}"}) + "\n")

        # Step 1: plan
        monkeypatch.setattr(sys, "argv", [
            "amplifier-research-resume",
            "plan",
            "--partial-results", str(partial_path),
            "--full-input", str(full_input_path),
            "--approaches", "A0,A4",
            "--output-manifest", str(manifest_path),
        ])
        cli_main()

        assert manifest_path.exists()
        manifest_data = json.loads(manifest_path.read_text())
        assert manifest_data["totals"]["never_started_count"] == 4
        assert manifest_data["totals"]["errored_count"] == 1
        assert manifest_data["totals"]["rerun_count"] == 5

        # Step 2: subset
        monkeypatch.setattr(sys, "argv", [
            "amplifier-research-resume",
            "subset",
            "--manifest", str(manifest_path),
            "--full-input", str(full_input_path),
            "--output-jsonl", str(rerun_path),
        ])
        cli_main()

        assert rerun_path.exists()
        rerun_items = [json.loads(l) for l in rerun_path.read_text().splitlines() if l.strip()]
        assert len(rerun_items) == 5  # 1 errored + 4 never_started

        # Step 3: mock new run (simulate the sweep producing results for rerun items)
        rerun_item_ids = [item["id"] for item in rerun_items]
        new_records = []
        for item_id in rerun_item_ids:
            for approach in approaches:
                new_records.append({
                    "item_id": item_id,
                    "approach_id": approach,
                    "response": LONG_RESPONSE,
                    "correct_by_judge": True,
                })
        _write_jsonl(new_results_path, new_records)

        # Step 4: merge
        monkeypatch.setattr(sys, "argv", [
            "amplifier-research-resume",
            "merge",
            "--manifest", str(manifest_path),
            "--partial-results", str(partial_path),
            "--new-results", str(new_results_path),
            "--output-merged", str(merged_path),
        ])
        cli_main()

        assert merged_path.exists()
        merged_records = [json.loads(l) for l in merged_path.read_text().splitlines() if l.strip()]

        # 5 clean items × 2 approaches (preserved) + 5 rerun × 2 approaches (new) = 20
        assert len(merged_records) == 20

        # Step 5: Verify all 10 items are present
        item_ids_in_merged = {r["item_id"] for r in merged_records}
        assert item_ids_in_merged == set(all_ids)
