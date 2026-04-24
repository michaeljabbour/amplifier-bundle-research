"""
mount.py — Amplifier module mount point.

Registers the ``experiment_resume`` tool with the Amplifier coordinator so
that any session loading this module can invoke plan / subset / merge
operations directly from the assistant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class ExperimentResumeMount:
    """Tool mount for the experiment resume/repair capability.

    Implements the Amplifier Tool protocol (name / description / input_schema
    / execute).  The three subcommands (plan, subset, merge) are exposed via
    the ``operation`` parameter.
    """

    @property
    def name(self) -> str:
        return "experiment_resume"

    @property
    def description(self) -> str:
        return (
            "Resume or repair an aborted experiment run.  Three operations:\n"
            "- plan: Categorise a partial results.jsonl into clean/errored/never-started "
            "and produce a resume_manifest.json.\n"
            "- subset: Write a subset jsonl containing only items that need re-running "
            "(errored ∪ never-started).\n"
            "- merge: Combine preserved records from the original partial file with new "
            "results from a resume run into a unified results.jsonl.\n\n"
            "Run plan first, then subset to prepare the re-run input, then merge after "
            "the sweep completes."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["plan", "subset", "merge"],
                    "description": "Which operation to perform.",
                },
                "partial_results": {
                    "type": "string",
                    "description": "Path to results.jsonl.partial (for 'plan' and 'merge').",
                },
                "full_input": {
                    "type": "string",
                    "description": "Path to the original full-input jsonl (for plan and subset).",
                },
                "approaches": {
                    "type": "string",
                    "description": "Comma-separated approach IDs, e.g. 'A0,A4' (for 'plan').",
                },
                "output_manifest": {
                    "type": "string",
                    "description": "Where to write the resume manifest JSON (for 'plan').",
                },
                "manifest": {
                    "type": "string",
                    "description": "Path to the resume_manifest.json (for 'subset' and 'merge').",
                },
                "output_jsonl": {
                    "type": "string",
                    "description": "Destination jsonl for items to rerun (for 'subset').",
                },
                "new_results": {
                    "type": "string",
                    "description": "Path to results.jsonl from the resume run (for 'merge').",
                },
                "output_merged": {
                    "type": "string",
                    "description": "Destination for the unified merged results.jsonl (for merge).",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        """Execute the requested operation and return a ToolResult-compatible dict."""
        from pathlib import Path

        operation = input_data.get("operation")

        try:
            if operation == "plan":
                from .plan import categorize_records

                approaches = [a.strip() for a in str(input_data.get("approaches", "")).split(",")]
                manifest = categorize_records(
                    partial_results=Path(input_data["partial_results"]),
                    full_input=Path(input_data["full_input"]),
                    approaches=approaches,
                )
                out_path = Path(input_data["output_manifest"])
                manifest.save(out_path)
                return {
                    "success": True,
                    "output": {
                        "manifest_path": str(out_path),
                        "totals": manifest.totals,
                    },
                }

            elif operation == "subset":
                from .manifest import ResumeManifest
                from .subset import write_subset

                manifest = ResumeManifest.load(Path(input_data["manifest"]))
                n = write_subset(
                    manifest=manifest,
                    full_input=Path(input_data["full_input"]),
                    output_jsonl=Path(input_data["output_jsonl"]),
                )
                return {
                    "success": True,
                    "output": {"items_written": n},
                }

            elif operation == "merge":
                from .manifest import ResumeManifest
                from .merge import merge_results

                manifest = ResumeManifest.load(Path(input_data["manifest"]))
                summary = merge_results(
                    manifest=manifest,
                    partial_results=Path(input_data["partial_results"]),
                    new_results=Path(input_data["new_results"]),
                    output_merged=Path(input_data["output_merged"]),
                )
                return {
                    "success": True,
                    "output": {
                        "report": summary.format_report(),
                        "has_gap": summary.has_gap,
                        "missing_items": summary.missing_items,
                    },
                }

            else:
                return {
                    "success": False,
                    "output": {
                        "error": f"Unknown operation: {operation!r}. Use plan, subset, or merge."
                    },
                }

        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"experiment_resume ({operation}) failed: {exc}"},
            }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the experiment_resume tool with the Amplifier coordinator."""
    tool = ExperimentResumeMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-resume",
        "version": "0.1.0",
        "provides": [tool.name],
    }
