"""
mount.py — Amplifier module mount point for tool-experiment-block-hypothesis.

Registers the ``block_hypothesis`` tool with the Amplifier coordinator so
that any session loading this module can invoke block-hypothesis evaluations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class BlockHypothesisMount:
    """Tool mount for the experiment block-hypothesis evaluation capability.

    Implements the Amplifier Tool protocol (name / description / input_schema /
    execute).  All heavy lifting is delegated to the submodules.
    """

    @property
    def name(self) -> str:
        return "block_hypothesis"

    @property
    def description(self) -> str:
        return (
            "Scientific evaluation of persistent reflection blocks. "
            "Analyses which rules in a block actually fire, compares "
            "conditions via ablation, checks per-domain sensitivity, and "
            "applies pre-registered thresholds to yield a structured verdict.\n"
            "Operations:\n"
            "- analyze_rule_firing: Per-rule heuristic firing analysis against "
            "stage_traces.jsonl.\n"
            "- ablation_summary: Multi-condition comparison table (paired Δ, "
            "McNemar p, empty rate, help:hurt).\n"
            "- domain_sensitivity: Per-category help/hurt rates with BH-FDR "
            "correction.\n"
            "- block_evaluation_verdict: Apply pre-registered thresholds → "
            "WORKS / HETEROGENEOUS / DOES_NOT_WORK / UNDERPOWERED verdict.\n\n"
            "Primary use case: rigorously determine whether a reflection block "
            "improves benchmark performance and which rules are responsible."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "analyze_rule_firing",
                        "ablation_summary",
                        "domain_sensitivity",
                        "block_evaluation_verdict",
                    ],
                    "description": "Which analysis operation to perform.",
                },
                "block_path": {
                    "type": "string",
                    "description": "Path to the block JSON file (for analyze_rule_firing).",
                },
                "traces_path": {
                    "type": "string",
                    "description": "Path to stage_traces.jsonl (for analyze_rule_firing).",
                },
                "conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of condition names (for ablation_summary).",
                },
                "results_dir": {
                    "type": "string",
                    "description": "Directory with per-condition .jsonl files "
                    "(for ablation_summary).",
                },
                "results_path": {
                    "type": "string",
                    "description": "Path to results.jsonl (for domain_sensitivity).",
                },
                "items_path": {
                    "type": "string",
                    "description": "Path to items.jsonl with category field "
                    "(for domain_sensitivity).",
                },
                "baseline_approach": {
                    "type": "string",
                    "description": "Baseline approach ID (for domain_sensitivity, default: A0).",
                },
                "treatment_approach": {
                    "type": "string",
                    "description": "Treatment approach ID (for domain_sensitivity, default: A12).",
                },
                "ablation_dir": {
                    "type": "string",
                    "description": "Directory with split subdirs (for block_evaluation_verdict).",
                },
                "baseline_condition": {
                    "type": "string",
                    "description": "Baseline condition stem "
                    "(for block_evaluation_verdict, default: C0).",
                },
                "treatment_condition": {
                    "type": "string",
                    "description": "Treatment condition stem (for block_evaluation_verdict).",
                },
                "threshold_paired_delta": {
                    "type": "number",
                    "description": "Minimum net delta pp for WORKS (default: 5.0).",
                },
                "threshold_substantive_delta": {
                    "type": "number",
                    "description": "Minimum substantive delta pp for WORKS (default: 10.0).",
                },
                "threshold_fdr": {
                    "type": "number",
                    "description": "Maximum McNemar p for WORKS (default: 0.05).",
                },
                "threshold_replication_splits": {
                    "type": "integer",
                    "description": "Minimum positive-direction splits for WORKS (default: 3).",
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional output file path.",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        """Execute the requested block-hypothesis operation."""
        operation = input_data.get("operation")
        output_path = input_data.get("output_path")

        try:
            if operation == "analyze_rule_firing":
                return await self._analyze_rule_firing(input_data, output_path)
            elif operation == "ablation_summary":
                return await self._ablation_summary(input_data, output_path)
            elif operation == "domain_sensitivity":
                return await self._domain_sensitivity(input_data, output_path)
            elif operation == "block_evaluation_verdict":
                return await self._block_evaluation_verdict(input_data, output_path)
            else:
                return {
                    "success": False,
                    "output": {"error": f"Unknown operation={operation!r}."},
                }
        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"block_hypothesis ({operation}) failed: {exc}"},
            }

    async def _analyze_rule_firing(self, input_data: dict, output_path: str | None) -> dict:
        import json
        from pathlib import Path

        from amplifier_research_block_hypothesis.rule_firing import (
            analyze_rule_firing,
            rule_firing_to_markdown,
        )

        block_path = input_data.get("block_path", "")
        traces_path = input_data.get("traces_path", "")

        block = json.loads(Path(block_path).read_text(encoding="utf-8"))
        traces = [
            json.loads(line)
            for line in Path(traces_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        analysis = analyze_rule_firing(block, traces)
        report = rule_firing_to_markdown(block, analysis, output_path=output_path)

        return {
            "success": True,
            "output": {
                "analysis": analysis,
                "report_preview": report[:2000],
                "output_path": output_path,
            },
        }

    async def _ablation_summary(self, input_data: dict, output_path: str | None) -> dict:
        import json
        from pathlib import Path

        from amplifier_research_block_hypothesis.ablation import (
            ablation_to_markdown,
            compute_ablation_summary,
        )

        conditions = input_data.get("conditions", [])
        results_dir = Path(input_data.get("results_dir", ""))
        baseline = conditions[0] if conditions else "C0"

        conditions_results: dict[str, list[dict]] = {}
        for cond in conditions:
            cond_file = results_dir / f"{cond}.jsonl"
            if cond_file.exists():
                conditions_results[cond] = [
                    json.loads(line)
                    for line in cond_file.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]

        summary = compute_ablation_summary(conditions_results, baseline=baseline)
        report = ablation_to_markdown(summary, output_path=output_path)

        return {
            "success": True,
            "output": {
                "summary": summary,
                "report_preview": report[:2000],
                "output_path": output_path,
            },
        }

    async def _domain_sensitivity(self, input_data: dict, output_path: str | None) -> dict:
        import json
        from pathlib import Path

        from amplifier_research_block_hypothesis.domain import (
            compute_domain_sensitivity,
            domain_to_markdown,
        )

        results_path = input_data.get("results_path", "")
        items_path = input_data.get("items_path", "")
        baseline_approach = input_data.get("baseline_approach", "A0")
        treatment_approach = input_data.get("treatment_approach", "A12")

        results = [
            json.loads(line)
            for line in Path(results_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        items = [
            json.loads(line)
            for line in Path(items_path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        sensitivity = compute_domain_sensitivity(
            results, items, baseline_approach, treatment_approach
        )
        report = domain_to_markdown(sensitivity, output_path=output_path)

        return {
            "success": True,
            "output": {
                "sensitivity": sensitivity,
                "report_preview": report[:2000],
                "output_path": output_path,
            },
        }

    async def _block_evaluation_verdict(self, input_data: dict, output_path: str | None) -> dict:
        import json
        from pathlib import Path

        from amplifier_research_block_hypothesis.cli import _load_splits_from_ablation_dir
        from amplifier_research_block_hypothesis.verdict import compute_verdict

        ablation_dir = Path(input_data.get("ablation_dir", ""))
        baseline_condition = input_data.get("baseline_condition", "C0")
        treatment_condition = input_data.get("treatment_condition", "treatment")

        splits = _load_splits_from_ablation_dir(
            ablation_dir, baseline_condition, treatment_condition
        )

        verdict = compute_verdict(
            splits=splits,
            threshold_paired_delta=input_data.get("threshold_paired_delta", 5.0),
            threshold_substantive_delta=input_data.get("threshold_substantive_delta", 10.0),
            threshold_fdr=input_data.get("threshold_fdr", 0.05),
            threshold_replication_splits=input_data.get("threshold_replication_splits", 3),
        )

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(verdict, indent=2), encoding="utf-8")

        return {
            "success": True,
            "output": {
                "verdict": verdict["verdict"],
                "evidence": verdict["evidence"],
                "output_path": output_path,
            },
        }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the block_hypothesis tool with the Amplifier coordinator."""
    tool = BlockHypothesisMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-block-hypothesis",
        "version": "0.1.0",
        "provides": [tool.name],
    }
