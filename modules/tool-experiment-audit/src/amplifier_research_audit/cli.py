"""
cli.py — Standalone command-line interface for the experiment integrity audit.

Usage (single experiment):
    python -m amplifier_research_audit \\
        --experiment experiments/production/a12a_v2 \\
        --expected-items 300 \\
        --output audit_reports/a12a_v2_audit.md

Usage (batch):
    python -m amplifier_research_audit \\
        --experiments-root experiments/ \\
        --output audit_reports/full_audit.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import audit_experiment
from .report import generate_batch_report, generate_report


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amplifier_research_audit",
        description="Audit experiment directories for integrity issues.",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--experiment",
        type=Path,
        metavar="DIR",
        help="Single experiment directory to audit.",
    )
    mode.add_argument(
        "--experiments-root",
        type=Path,
        metavar="ROOT",
        help=(
            "Root directory to scan recursively.  Every sub-directory "
            "containing a results.jsonl is audited."
        ),
    )
    p.add_argument(
        "--expected-items",
        type=int,
        default=None,
        metavar="N",
        help="Expected number of distinct items (enables row-count check).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write report to FILE instead of stdout.",
    )
    return p


def main() -> None:
    """Entry point for ``python -m amplifier_research_audit`` and the installed script."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.experiment:
        result = audit_experiment(args.experiment, expected_n_items=args.expected_items)
        report = generate_report(result)
    else:
        # Batch mode: discover every directory that owns a results.jsonl
        root = args.experiments_root
        exp_dirs = sorted(
            {jsonl.parent for jsonl in root.rglob("results.jsonl")},
            key=lambda p: p.name,
        )
        if not exp_dirs:
            print(f"No results.jsonl files found under {root}", file=sys.stderr)
            sys.exit(1)

        results = [audit_experiment(d, expected_n_items=args.expected_items) for d in exp_dirs]
        report = generate_batch_report(results)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
