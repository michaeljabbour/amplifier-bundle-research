"""
mount.py — Amplifier module mount point.

Registers the ``experiment_stage_analyzer`` tool with the Amplifier coordinator
so that any session loading this module can invoke stage-trace analyses from
the assistant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class ExperimentStageAnalyzerMount:
    """Tool mount for the experiment stage-trace analyzer capability.

    Implements the Amplifier Tool protocol (name / description / input_schema /
    execute).  All heavy lifting is delegated to :mod:`ingest`, :mod:`categorize`,
    :mod:`analyze`, and :mod:`report`.
    """

    @property
    def name(self) -> str:
        return "experiment_stage_analyzer"

    @property
    def description(self) -> str:
        return (
            "Empty-response root-cause analysis for staged reflection experiments. "
            "Ingests stage_traces.jsonl (generator / critic / revert_decision) and "
            "categorizes each empty-final record by its failure-mode origin.\n"
            "Operations:\n"
            "- analyze: Full pipeline — categorize + hypothesis-test + Markdown report.\n"
            "- hypothesis_test: Return H1a/H1b verdicts as structured JSON.\n\n"
            "Primary use case: after a reflection-token sweep, determine whether empty "
            "responses originate in the generator stage, the critic stage, or the revert "
            "decision, and apply pre-registered H1a/H1b confirmation criteria."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze", "hypothesis_test"],
                    "description": "Which analysis operation to perform.",
                },
                "traces_path": {
                    "type": "string",
                    "description": "Filesystem path to the stage_traces.jsonl file.",
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional output file path (Markdown or JSON).",
                },
            },
            "required": ["operation", "traces_path"],
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        """Execute the requested stage-analysis operation."""
        operation = input_data.get("operation")
        traces_path = input_data.get("traces_path", "")
        output_path = input_data.get("output_path")

        try:
            from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
            from amplifier_research_stage_analyzer.categorize import categorize_empty
            from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

            records = ingest_stage_traces(traces_path)
            cat_result = categorize_empty(records)

            if operation == "hypothesis_test":
                hyp = test_h1_hypotheses(cat_result)
                out: dict[str, Any] = {
                    "h1a_confirmed": hyp["h1a_confirmed"],
                    "h1a_fraction": hyp["h1a_fraction"],
                    "h1b_confirmed": hyp["h1b_confirmed"],
                    "h1b_fraction": hyp["h1b_fraction"],
                    "evidence_count": len(hyp["evidence"]),
                }
                return {"success": True, "output": out}

            elif operation == "analyze":
                from amplifier_research_stage_analyzer.report import generate_report

                hyp = test_h1_hypotheses(cat_result)
                total_empty = sum(cat_result["counts"].values())
                analysis = {
                    "categorize": cat_result,
                    "hypothesis": hyp,
                    "total_records": len(records),
                    "total_empty": total_empty,
                }
                report_text = generate_report(analysis, output_path=output_path)
                return {
                    "success": True,
                    "output": {
                        "report": report_text[:2000],  # truncate for tool response
                        "output_path": output_path,
                        "total_records": len(records),
                        "total_empty": total_empty,
                        "h1a_confirmed": hyp["h1a_confirmed"],
                        "h1b_confirmed": hyp["h1b_confirmed"],
                    },
                }

            return {
                "success": False,
                "output": {"error": f"Unknown operation={operation!r}."},
            }

        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"experiment_stage_analyzer ({operation}) failed: {exc}"},
            }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the experiment_stage_analyzer tool with the Amplifier coordinator."""
    tool = ExperimentStageAnalyzerMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-stage-analyzer",
        "version": "0.1.0",
        "provides": [tool.name],
    }
