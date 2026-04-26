"""
cli.py — amplifier-research-stage-analyzer command-line interface.

Subcommand structure:
  amplifier-research-stage-analyzer analyze         --traces PATH --output PATH
  amplifier-research-stage-analyzer hypothesis-test --traces PATH --output PATH
"""

from __future__ import annotations

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# 'analyze' subcommand
# ---------------------------------------------------------------------------


def _cmd_analyze(args: argparse.Namespace) -> None:
    """Run full analysis: ingest → categorize → hypothesis test → markdown report."""
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
    from amplifier_research_stage_analyzer.categorize import categorize_empty
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces
    from amplifier_research_stage_analyzer.report import generate_report

    records = ingest_stage_traces(args.traces)
    cat_result = categorize_empty(records)
    hyp_result = test_h1_hypotheses(cat_result)

    total_empty = sum(cat_result["counts"].values())
    analysis = {
        "categorize": cat_result,
        "hypothesis": hyp_result,
        "total_records": len(records),
        "total_empty": total_empty,
    }

    report_text = generate_report(analysis, output_path=args.output)

    if args.output:
        print(f"Report written to: {args.output}")
    else:
        print(report_text)


# ---------------------------------------------------------------------------
# 'hypothesis-test' subcommand
# ---------------------------------------------------------------------------


def _cmd_hypothesis_test(args: argparse.Namespace) -> None:
    """Ingest traces, categorize, and emit hypothesis-test verdicts as JSON."""
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
    from amplifier_research_stage_analyzer.categorize import categorize_empty
    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces

    records = ingest_stage_traces(args.traces)
    cat_result = categorize_empty(records)
    hyp_result = test_h1_hypotheses(cat_result)

    # Serialize evidence to JSON-safe form (list of item_id strings)
    output_data = {
        "h1a_confirmed": hyp_result["h1a_confirmed"],
        "h1a_fraction": hyp_result["h1a_fraction"],
        "h1b_confirmed": hyp_result["h1b_confirmed"],
        "h1b_fraction": hyp_result["h1b_fraction"],
        "evidence": [{"item_id": ev.get("item_id", "")} for ev in hyp_result["evidence"]],
    }

    json_text = json.dumps(output_data, indent=2)

    if args.output:
        from pathlib import Path

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_text, encoding="utf-8")
        print(f"Verdicts written to: {args.output}")
    else:
        print(json_text)


# ---------------------------------------------------------------------------
# Parser builder
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="amplifier-research-stage-analyzer",
        description=(
            "Stage-trace empty-response root-cause analyzer. "
            "Categorizes failures by stage origin and applies pre-registered H1 criteria."
        ),
    )
    root.set_defaults(func=None)
    subs = root.add_subparsers(dest="command", metavar="SUBCOMMAND")

    # --- analyze ---
    ana = subs.add_parser(
        "analyze",
        help="Full pipeline: ingest → categorize → hypothesis-test → Markdown report",
    )
    ana.add_argument(
        "--traces",
        required=True,
        metavar="PATH",
        help="Path to stage_traces.jsonl",
    )
    ana.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Output path for Markdown report (prints to stdout if omitted)",
    )
    ana.set_defaults(func=_cmd_analyze)

    # --- hypothesis-test ---
    ht = subs.add_parser(
        "hypothesis-test",
        help="Ingest + categorize + emit H1a/H1b verdicts as JSON",
    )
    ht.add_argument(
        "--traces",
        required=True,
        metavar="PATH",
        help="Path to stage_traces.jsonl",
    )
    ht.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Output path for verdicts JSON (prints to stdout if omitted)",
    )
    ht.set_defaults(func=_cmd_hypothesis_test)

    return root


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for ``amplifier-research-stage-analyzer``."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
