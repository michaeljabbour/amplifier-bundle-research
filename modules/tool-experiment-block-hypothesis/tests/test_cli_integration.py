"""
test_cli_integration.py — End-to-end smoke tests for each CLI subcommand.

Creates synthetic fixture files in a temp dir and runs each subcommand
via the Python API (not subprocess) to keep tests fast.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Fixture helpers
# ─────────────────────────────────────────────────────────────────────────────


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _make_block() -> dict:
    return {
        "name": "test_block",
        "rules": [
            {
                "mechanism": "ARITHMETIC_ERROR",
                "trigger": "always check arithmetic in responses",
                "action": "recheck arithmetic carefully",
                "token": "RT_CHECK_ARITHMETIC",
            },
            {
                "mechanism": "FACTUAL_ERROR",
                "trigger": "verify factual claims before concluding",
                "action": "double check factual accuracy",
                "token": "RT_VERIFY_FACTUAL",
            },
        ],
    }


def _make_traces(n: int = 10) -> list[dict]:
    """Generate n synthetic stage traces, half with relevant critic content."""
    traces = []
    for i in range(n):
        critic_text = "arithmetic needs checking here" if i % 2 == 0 else "looks correct"
        traces.append(
            {
                "item_id": f"item_{i}",
                "approach_id": "A12a",
                "approach_name": "test",
                "stages": {
                    "generator": {
                        "output": "answer",
                        "output_length": 6,
                        "latency_ms": 100.0,
                        "cost_usd": 0.001,
                        "is_empty": False,
                        "is_truncated": False,
                    },
                    "critic": {"output": critic_text},
                    "revert_decision": {"reverted": False},
                },
                "final_response_length": 100,
                "final_is_empty": False,
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        )
    return traces


def _make_results(n: int = 20, flip_start: int = 10) -> list[dict]:
    return [
        {"item_id": f"item_{i}", "correct_by_judge": i >= flip_start, "is_empty": False}
        for i in range(n)
    ]


def _make_items(n: int = 20, categories: list[str] | None = None) -> list[dict]:
    if categories is None:
        categories = ["Math"] * 10 + ["History"] * 10
    return [{"item_id": f"item_{i}", "category": categories[i % len(categories)]} for i in range(n)]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: analyze-rule-firing subcommand
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_analyze_rule_firing_smoke():
    """analyze-rule-firing produces a markdown report with rule sections."""
    from amplifier_research_block_hypothesis.cli import _cmd_analyze_rule_firing
    import argparse

    with tempfile.TemporaryDirectory() as tmpdir:
        block_path = Path(tmpdir) / "block.json"
        traces_path = Path(tmpdir) / "stage_traces.jsonl"
        output_path = Path(tmpdir) / "rule_analysis.md"

        _write_json(block_path, _make_block())
        _write_jsonl(traces_path, _make_traces(10))

        args = argparse.Namespace(
            block=str(block_path),
            traces=str(traces_path),
            output=str(output_path),
        )
        _cmd_analyze_rule_firing(args)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "RT_CHECK_ARITHMETIC" in content or "ARITHMETIC" in content
        assert "fires" in content.lower() or "fire" in content.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: ablation-summary subcommand
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_ablation_summary_smoke():
    """ablation-summary reads a results dir and emits a comparison table."""
    from amplifier_research_block_hypothesis.cli import _cmd_ablation_summary
    import argparse

    with tempfile.TemporaryDirectory() as tmpdir:
        results_dir = Path(tmpdir) / "results"
        results_dir.mkdir()
        output_path = Path(tmpdir) / "ablation.md"

        n = 20
        _write_jsonl(results_dir / "C0.jsonl", _make_results(n, flip_start=8))
        _write_jsonl(results_dir / "C3_block.jsonl", _make_results(n, flip_start=12))

        args = argparse.Namespace(
            conditions="C0,C3_block",
            results_dir=str(results_dir),
            output=str(output_path),
        )
        _cmd_ablation_summary(args)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "C3_block" in content


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: domain-sensitivity subcommand
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_domain_sensitivity_smoke():
    """domain-sensitivity reads results + items and emits per-category output."""
    from amplifier_research_block_hypothesis.cli import _cmd_domain_sensitivity
    import argparse

    with tempfile.TemporaryDirectory() as tmpdir:
        n = 20
        item_ids = [f"item_{i}" for i in range(n)]
        categories = ["Math"] * 10 + ["History"] * 10

        # Build results: two approaches per item
        results_records = []
        for i, iid in enumerate(item_ids):
            results_records.append({"item_id": iid, "approach_id": "A0", "correct_by_judge": i < 10})
            results_records.append({"item_id": iid, "approach_id": "A12", "correct_by_judge": i < 14})

        items_records = [{"item_id": iid, "category": cat}
                         for iid, cat in zip(item_ids, categories)]

        results_path = Path(tmpdir) / "results.jsonl"
        items_path = Path(tmpdir) / "items.jsonl"
        output_path = Path(tmpdir) / "domain.md"

        _write_jsonl(results_path, results_records)
        _write_jsonl(items_path, items_records)

        args = argparse.Namespace(
            results=str(results_path),
            items=str(items_path),
            baseline_approach="A0",
            treatment_approach="A12",
            output=str(output_path),
        )
        _cmd_domain_sensitivity(args)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "Math" in content or "History" in content


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: block-evaluation-verdict subcommand
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_block_evaluation_verdict_smoke():
    """block-evaluation-verdict reads an ablation dir and emits a verdict JSON."""
    from amplifier_research_block_hypothesis.cli import _cmd_block_evaluation_verdict
    import argparse

    with tempfile.TemporaryDirectory() as tmpdir:
        ablation_dir = Path(tmpdir) / "ablation"
        ablation_dir.mkdir()
        output_path = Path(tmpdir) / "verdict.json"

        # 3 splits: each with a results file for C0 and treatment
        for split_i in range(3):
            split_dir = ablation_dir / f"split_{split_i}"
            split_dir.mkdir()
            n = 100
            _write_jsonl(split_dir / "C0.jsonl", [
                {"item_id": f"item_{j}", "correct_by_judge": j < 40, "is_empty": False}
                for j in range(n)
            ])
            _write_jsonl(split_dir / "treatment.jsonl", [
                {"item_id": f"item_{j}", "correct_by_judge": j < 55, "is_empty": False}
                for j in range(n)
            ])

        args = argparse.Namespace(
            ablation_dir=str(ablation_dir),
            baseline_condition="C0",
            treatment_condition="treatment",
            threshold_paired_delta=5.0,
            threshold_substantive_delta=10.0,
            threshold_fdr=0.05,
            threshold_replication_splits=3,
            output=str(output_path),
        )
        _cmd_block_evaluation_verdict(args)

        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding="utf-8"))
        assert "verdict" in data
        assert data["verdict"] in {"WORKS", "HETEROGENEOUS", "DOES_NOT_WORK", "UNDERPOWERED"}
