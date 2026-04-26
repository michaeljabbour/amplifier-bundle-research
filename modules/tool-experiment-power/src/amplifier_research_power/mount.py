"""
mount.py — Amplifier module mount point.

Registers the ``experiment_power`` tool with the Amplifier coordinator so
that any session loading this module can invoke power analyses directly from
the assistant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass  # avoid hard dep on amplifier_core at import time


class ExperimentPowerMount:
    """Tool mount for the experiment power-analysis capability.

    Implements the Amplifier Tool protocol (name / description / input_schema /
    execute).  All heavy lifting is delegated to :mod:`mcnemar` and :mod:`ttest`.
    """

    @property
    def name(self) -> str:
        return "experiment_power"

    @property
    def description(self) -> str:
        return (
            "Statistical power analysis for experiment design. "
            "Supports McNemar paired-binary tests and independent t-tests.\n"
            "Operations:\n"
            "- required_n: Compute required sample size given effect size and target power.\n"
            "- mde: Minimum detectable effect at given n and target power.\n"
            "- post_hoc: Achieved power for a completed or planned study.\n"
            "- sensitivity: Cross-product table of required n's over assumption ranges.\n\n"
            "Primary use case: pre-register a sample size for a held-out replication "
            "experiment using discordant-pair rates from a pilot study."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["required_n", "mde", "post_hoc", "sensitivity"],
                    "description": "Which power-analysis operation to perform.",
                },
                "test_type": {
                    "type": "string",
                    "enum": ["mcnemar", "ttest"],
                    "description": "Statistical test (default: 'mcnemar').",
                },
                # McNemar parameters
                "p_disc": {
                    "type": "number",
                    "description": "(McNemar) Probability of a discordant pair, in (0, 1).",
                },
                "p_help_given_disc": {
                    "type": "number",
                    "description": "(McNemar) P(help | discordant), in [0.5, 1.0].",
                },
                # Shared / t-test parameters
                "n": {
                    "type": "integer",
                    "description": "Sample size (for mde and post_hoc).",
                },
                "cohens_d": {
                    "type": "number",
                    "description": "(t-test) Cohen's d effect size.",
                },
                "alpha": {
                    "type": "number",
                    "description": "Type-I error rate (default: 0.05).",
                },
                "power": {
                    "type": "number",
                    "description": "Target power (default: 0.80).",
                },
                # Sensitivity table
                "p_disc_range": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "(sensitivity) List of p_disc values to vary.",
                },
                "p_help_given_disc_range": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "(sensitivity) List of p_help_given_disc values.",
                },
                "target_pp": {
                    "type": "number",
                    "description": "(sensitivity) Reference target effect in pp.",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> Any:  # noqa: C901
        """Execute the requested power-analysis operation."""
        operation = input_data.get("operation")
        test_type = input_data.get("test_type", "mcnemar")
        alpha = float(input_data.get("alpha", 0.05))
        power_target = float(input_data.get("power", 0.80))

        try:
            if test_type == "mcnemar":
                from .mcnemar import (
                    mde_mcnemar,
                    power_mcnemar,
                    required_n_mcnemar,
                    sensitivity_table,
                )

                if operation == "required_n":
                    n = required_n_mcnemar(
                        p_disc=float(input_data["p_disc"]),
                        p_help_given_disc=float(input_data["p_help_given_disc"]),
                        alpha=alpha,
                        power=power_target,
                    )
                    return {"success": True, "output": {"required_n": n}}

                elif operation == "mde":
                    mde_pp = mde_mcnemar(
                        n=int(input_data["n"]),
                        p_disc=float(input_data["p_disc"]),
                        alpha=alpha,
                        power=power_target,
                    )
                    return {"success": True, "output": {"mde_pp": mde_pp}}

                elif operation == "post_hoc":
                    pwr = power_mcnemar(
                        n=int(input_data["n"]),
                        p_disc=float(input_data["p_disc"]),
                        p_help_given_disc=float(input_data["p_help_given_disc"]),
                        alpha=alpha,
                    )
                    return {"success": True, "output": {"power": pwr}}

                elif operation == "sensitivity":
                    df = sensitivity_table(
                        p_disc_range=[float(x) for x in input_data["p_disc_range"]],
                        p_help_given_disc_range=[
                            float(x) for x in input_data["p_help_given_disc_range"]
                        ],
                        target_pp=float(input_data.get("target_pp", 5.0)),
                        alpha=alpha,
                        power=power_target,
                    )
                    return {"success": True, "output": {"table": df.to_dict(orient="records")}}

            elif test_type == "ttest":
                from .ttest import mde_ttest, power_ttest, required_n_ttest

                if operation == "required_n":
                    n = required_n_ttest(
                        cohens_d=float(input_data["cohens_d"]),
                        alpha=alpha,
                        power=power_target,
                    )
                    return {"success": True, "output": {"required_n": n}}

                elif operation == "mde":
                    d = mde_ttest(
                        n_per_group=int(input_data["n"]),
                        alpha=alpha,
                        power=power_target,
                    )
                    return {"success": True, "output": {"mde_cohens_d": d}}

                elif operation == "post_hoc":
                    pwr = power_ttest(
                        n_per_group=int(input_data["n"]),
                        cohens_d=float(input_data["cohens_d"]),
                        alpha=alpha,
                    )
                    return {"success": True, "output": {"power": pwr}}

            return {
                "success": False,
                "output": {"error": f"Unknown operation={operation!r} or test_type={test_type!r}."},
            }

        except Exception as exc:
            return {
                "success": False,
                "output": {"error": f"experiment_power ({operation}) failed: {exc}"},
            }


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Register the experiment_power tool with the Amplifier coordinator."""
    tool = ExperimentPowerMount()
    await coordinator.mount("tools", tool, name=tool.name)
    return {
        "name": "tool-experiment-power",
        "version": "0.1.0",
        "provides": [tool.name],
    }
