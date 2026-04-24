"""
cli.py — Single binary ``amplifier-research-resume`` with three subcommands:

  plan    Categorise partial results and produce a resume manifest.
  subset  Write items-to-rerun jsonl from a manifest.
  merge   Combine preserved + new records into unified results.

Usage::

    amplifier-research-resume plan \\
        --partial-results experiments/foo/results.jsonl.partial \\
        --full-input data/reserved/dev.jsonl \\
        --approaches A0,A4 \\
        --output-manifest experiments/foo/resume_manifest.json

    amplifier-research-resume subset \\
        --manifest experiments/foo/resume_manifest.json \\
        --full-input data/reserved/dev.jsonl \\
        --output-jsonl data/reserved/dev_resume.jsonl

    amplifier-research-resume merge \\
        --manifest experiments/foo/resume_manifest.json \\
        --partial-results experiments/foo/results.jsonl.partial \\
        --new-results experiments/foo_resume/results.jsonl \\
        --output-merged experiments/foo/results.merged.jsonl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .manifest import ResumeManifest
from .merge import merge_results
from .plan import categorize_records
from .subset import write_subset

# ---------------------------------------------------------------------------
# Subcommand: plan
# ---------------------------------------------------------------------------


def _cmd_plan(args: argparse.Namespace) -> None:
    """Run the plan subcommand."""
    approaches = [a.strip() for a in args.approaches.split(",")]

    manifest = categorize_records(
        partial_results=args.partial_results,
        full_input=args.full_input,
        approaches=approaches,
    )

    out = Path(args.output_manifest)
    manifest.save(out)

    t = manifest.totals
    print(f"Resume manifest written to: {out}")
    print(f"  clean_complete: {t['clean_complete_count']}")
    print(f"  errored:        {t['errored_count']}")
    print(f"  never_started:  {t['never_started_count']}")
    print(f"  rerun_count:    {t['rerun_count']}")
    print(f"  expected_total: {t['expected_full_count']}")


# ---------------------------------------------------------------------------
# Subcommand: subset
# ---------------------------------------------------------------------------


def _cmd_subset(args: argparse.Namespace) -> None:
    """Run the subset subcommand."""
    manifest = ResumeManifest.load(args.manifest)
    n = write_subset(
        manifest=manifest,
        full_input=args.full_input,
        output_jsonl=args.output_jsonl,
    )
    print(f"Subset written to: {args.output_jsonl}  ({n} items)")


# ---------------------------------------------------------------------------
# Subcommand: merge
# ---------------------------------------------------------------------------


def _cmd_merge(args: argparse.Namespace) -> None:
    """Run the merge subcommand."""
    manifest = ResumeManifest.load(args.manifest)
    summary = merge_results(
        manifest=manifest,
        partial_results=args.partial_results,
        new_results=args.new_results,
        output_merged=args.output_merged,
    )
    print(f"Merged file written to: {args.output_merged}")
    print(summary.format_report())
    if summary.has_gap:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amplifier-research-resume",
        description="Experiment resume/repair capability for Amplifier research runs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- plan ----
    p_plan = subparsers.add_parser(
        "plan",
        help="Categorise partial results and produce a resume manifest.",
    )
    p_plan.add_argument(
        "--partial-results",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to results.jsonl.partial (or results.jsonl from aborted run).",
    )
    p_plan.add_argument(
        "--full-input",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to the original full-input jsonl (id field per item).",
    )
    p_plan.add_argument(
        "--approaches",
        required=True,
        metavar="A0,A4",
        help="Comma-separated list of approach IDs that were running.",
    )
    p_plan.add_argument(
        "--output-manifest",
        type=Path,
        required=True,
        metavar="FILE",
        help="Where to write the resume_manifest.json.",
    )

    # ---- subset ----
    p_subset = subparsers.add_parser(
        "subset",
        help="Write items-to-rerun jsonl from a manifest.",
    )
    p_subset.add_argument(
        "--manifest",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to resume_manifest.json produced by 'plan'.",
    )
    p_subset.add_argument(
        "--full-input",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to the original full-input jsonl.",
    )
    p_subset.add_argument(
        "--output-jsonl",
        type=Path,
        required=True,
        metavar="FILE",
        help="Destination jsonl with only items that need re-running.",
    )

    # ---- merge ----
    p_merge = subparsers.add_parser(
        "merge",
        help="Combine preserved + new records into unified results.",
    )
    p_merge.add_argument(
        "--manifest",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to the resume_manifest.json.",
    )
    p_merge.add_argument(
        "--partial-results",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to the original partial results (source of preserved records).",
    )
    p_merge.add_argument(
        "--new-results",
        type=Path,
        required=True,
        metavar="FILE",
        help="Path to results.jsonl from the resume run.",
    )
    p_merge.add_argument(
        "--output-merged",
        type=Path,
        required=True,
        metavar="FILE",
        help="Destination for the unified merged results.jsonl.",
    )

    return parser


def main() -> None:
    """Entry point for ``amplifier-research-resume`` and ``python -m amplifier_research_resume``."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "plan":
        _cmd_plan(args)
    elif args.command == "subset":
        _cmd_subset(args)
    elif args.command == "merge":
        _cmd_merge(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
