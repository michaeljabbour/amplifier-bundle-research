"""
mount.py — Amplifier module mount point.

Registers the ``experiment_provenance_check`` tool with the Amplifier coordinator
so that any session loading this module can invoke provenance audits from
the assistant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class ExperimentProvenanceCheckMount:
    """
    Tool mount for the experiment provenance-check capability.

    Implements the Amplifier Tool protocol (name / description / input_schema /
    execute).  All heavy lifting is delegated to :mod:`ast_walker`,
    :mod:`git_check`, and :mod:`report`.
    """

    @property
    def name(self) -> str:
        return "experiment_provenance_check"

    @property
    def description(self) -> str:
        return (
            "Pre-experiment data provenance audit. "
            "Parses a Python script's source with AST to discover all referenced data "
            "files, then checks each file against git to classify it as "
            "TRACKED / UNTRACKED / MISSING / IN_GITIGNORE. "
            "Emits a Markdown report highlighting integrity gaps.\n\n"
            "Operations:\n"
            "- audit_script: Full pipeline — parse script, check files, emit report.\n"
            "- check_files: Lightweight — check a list of files directly.\n"
            "- pre_experiment_gate: Hard gate — fail if any UNTRACKED file found.\n\n"
            "Primary use case: before running an experiment, verify that all input "
            "data files are committed to git. Prevents reproducibility gaps like the "
            "hle_handcrafted.json gap discovered in commit e189188."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["audit_script", "check_files", "pre_experiment_gate"],
                    "description": "Which provenance operation to perform.",
                },
                "script_path": {
                    "type": "string",
                    "description": "Filesystem path to the Python script to audit.",
                },
                "repo_path": {
                    "type": "string",
                    "description": "Root of the git repository.",
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths for check_files operation.",
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional output file path for the Markdown report.",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        """Execute the requested provenance-check operation."""
        operation = input_data.get("operation")
        script_path = input_data.get("script_path", "")
        repo_path = input_data.get("repo_path", "")
        files = input_data.get("files", [])
        output_path = input_data.get("output_path")

        try:
            from amplifier_research_provenance_check.ast_walker import walk_script
            from amplifier_research_provenance_check.git_check import (
                FileStatus,
                check_files,
            )
            from amplifier_research_provenance_check.report import generate_report

            if operation == "audit_script":
                from pathlib import Path

                source = Path(script_path).read_text(encoding="utf-8")
                discovered = walk_script(source)
                results = check_files(discovered, repo_path)
                report_text = generate_report(
                    results,
                    script_path=script_path,
                    repo_path=repo_path,
                )
                if output_path:
                    from pathlib import Path as _Path

                    _Path(output_path).write_text(report_text, encoding="utf-8")
                n_untracked = sum(s == FileStatus.UNTRACKED for s in results.values())
                return {
                    "success": True,
                    "output": {
                        "total_files": len(results),
                        "n_untracked": n_untracked,
                        "n_missing": sum(s == FileStatus.MISSING for s in results.values()),
                        "n_tracked": sum(s == FileStatus.TRACKED for s in results.values()),
                        "report_preview": report_text[:2000],
                        "output_path": output_path,
                    },
                }

            elif operation == "check_files":
                results = check_files(list(files), repo_path)
                return {
                    "success": True,
                    "output": {p: s.value for p, s in results.items()},
                }

            elif operation == "pre_experiment_gate":
                from pathlib import Path

                source = Path(script_path).read_text(encoding="utf-8")
                discovered = walk_script(source)
                results = check_files(discovered, repo_path)
                n_untracked = sum(s == FileStatus.UNTRACKED for s in results.values())
                n_missing = sum(s == FileStatus.MISSING for s in results.values())
                gate_passed = n_untracked == 0 and n_missing == 0
                return {
                    "success": gate_passed,
                    "output": {
                        "gate_passed": gate_passed,
                        "n_untracked": n_untracked,
                        "n_missing": n_missing,
                        "untracked_files": [
                            p for p, s in results.items() if s == FileStatus.UNTRACKED
                        ],
                        "missing_files": [p for p, s in results.items() if s == FileStatus.MISSING],
                    },
                }

            return {
                "success": False,
                "output": {"error": f"Unknown operation={operation!r}."},
            }

        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"experiment_provenance_check ({operation}) failed: {exc}"},
            }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the experiment_provenance_check tool with the Amplifier coordinator."""
    tool = ExperimentProvenanceCheckMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-provenance-check",
        "version": "0.1.0",
        "provides": [tool.name],
    }
