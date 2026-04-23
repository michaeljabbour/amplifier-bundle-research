"""
mount.py — Amplifier module mount point.

Registers the ``experiment_audit`` tool with the Amplifier coordinator so that
any session loading this module can invoke integrity audits directly from the
assistant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class ExperimentAuditMount:
    """Tool mount for the experiment integrity audit capability.

    Implements the Amplifier Tool protocol (name / description / input_schema /
    execute).  All heavy lifting is delegated to :mod:`audit` and :mod:`report`.
    """

    @property
    def name(self) -> str:
        return "experiment_audit"

    @property
    def description(self) -> str:
        return (
            "Audit one or more experiment directories for integrity issues — "
            "including HANDLER_ERROR cascades, short/duplicate responses, "
            "missing judge labels, absent manifests, and implausible baseline accuracy. "
            "Returns a Markdown report with a PASS / FAIL / SUSPICIOUS verdict "
            "and per-check evidence.  Run before trusting any experiment's numbers."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "experiment_dir": {
                    "type": "string",
                    "description": (
                        "Path to a single experiment directory containing results.jsonl."
                    ),
                },
                "experiments_root": {
                    "type": "string",
                    "description": (
                        "Path to a root directory.  Every sub-directory with a "
                        "results.jsonl will be audited."
                    ),
                },
                "expected_items": {
                    "type": "integer",
                    "description": "Expected number of distinct items (enables row-count check).",
                },
            },
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        """Execute the audit and return a ToolResult-compatible dict."""
        from pathlib import Path

        from .audit import audit_experiment
        from .report import generate_batch_report, generate_report

        expected_n_items: int | None = input_data.get("expected_items")

        try:
            if "experiment_dir" in input_data:
                result = audit_experiment(
                    Path(input_data["experiment_dir"]),
                    expected_n_items=expected_n_items,
                )
                report = generate_report(result)
                verdict = result.verdict.value
            elif "experiments_root" in input_data:
                root = Path(input_data["experiments_root"])
                exp_dirs = sorted(
                    {jsonl.parent for jsonl in root.rglob("results.jsonl")},
                    key=lambda p: p.name,
                )
                results = [audit_experiment(d, expected_n_items=expected_n_items) for d in exp_dirs]
                report = generate_batch_report(results)
                fail_count = sum(1 for r in results if r.verdict.value == "FAIL")
                verdict = (
                    "FAIL"
                    if fail_count > 0
                    else (
                        "SUSPICIOUS"
                        if any(r.verdict.value == "SUSPICIOUS" for r in results)
                        else "PASS"
                    )
                )
            else:
                return {
                    "success": False,
                    "output": {"error": "Provide either experiment_dir or experiments_root."},
                }

            return {
                "success": True,
                "output": {"report": report, "verdict": verdict},
            }
        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"Audit failed: {exc}"},
            }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the experiment_audit tool with the Amplifier coordinator."""
    tool = ExperimentAuditMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-audit",
        "version": "0.1.0",
        "provides": [tool.name],
    }
