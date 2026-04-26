"""
cli.py — amplifier-research-block-hypothesis command-line interface.

Subcommand structure:
  amplifier-research-block-hypothesis analyze-rule-firing \
      --block PATH --traces PATH --output PATH

  amplifier-research-block-hypothesis ablation-summary \
      --conditions C0,C3_alone,... --results-dir PATH --output PATH

  amplifier-research-block-hypothesis domain-sensitivity \
      --results PATH --items PATH \
      --baseline-approach A0 --treatment-approach A12 --output PATH

  amplifier-research-block-hypothesis block-evaluation-verdict \
      --ablation-dir PATH \
      --baseline-condition C0 --treatment-condition treatment \
      --threshold-paired-delta 5.0 --threshold-substantive-delta 10.0 \
      --threshold-fdr 0.05 --threshold-replication-splits 3 \
      --output PATH
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_jsonl(path: str) -> list[dict]:
    """Load a .jsonl file into a list of dicts."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    records = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand 1: analyze-rule-firing
# ─────────────────────────────────────────────────────────────────────────────


def _cmd_analyze_rule_firing(args: argparse.Namespace) -> None:
    """Per-rule firing heuristics against stage traces."""
    from amplifier_research_block_hypothesis.rule_firing import (
        analyze_rule_firing,
        rule_firing_to_markdown,
    )

    block_path = Path(args.block)
    if not block_path.exists():
        raise FileNotFoundError(f"Block file not found: {args.block}")

    block = json.loads(block_path.read_text(encoding="utf-8"))
    traces = _load_jsonl(args.traces)

    analysis = analyze_rule_firing(block, traces)
    report = rule_firing_to_markdown(block, analysis, output_path=args.output)

    if args.output:
        print(f"Rule analysis written to: {args.output}")
    else:
        print(report)


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand 2: ablation-summary
# ─────────────────────────────────────────────────────────────────────────────


def _cmd_ablation_summary(args: argparse.Namespace) -> None:
    """Multi-condition ablation comparison."""
    from amplifier_research_block_hypothesis.ablation import (
        ablation_to_markdown,
        compute_ablation_summary,
    )

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    results_dir = Path(args.results_dir)
    if not results_dir.is_dir():
        raise FileNotFoundError(f"Results directory not found: {args.results_dir}")

    conditions_results: dict[str, list[dict]] = {}
    for cond in conditions:
        cond_file = results_dir / f"{cond}.jsonl"
        if cond_file.exists():
            conditions_results[cond] = _load_jsonl(str(cond_file))
        else:
            print(f"Warning: {cond_file} not found, skipping.", file=sys.stderr)

    # Determine baseline (first condition, usually "C0")
    baseline = conditions[0] if conditions else "C0"

    summary = compute_ablation_summary(conditions_results, baseline=baseline)
    report = ablation_to_markdown(summary, output_path=args.output)

    if args.output:
        print(f"Ablation summary written to: {args.output}")
    else:
        print(report)


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand 3: domain-sensitivity
# ─────────────────────────────────────────────────────────────────────────────


def _cmd_domain_sensitivity(args: argparse.Namespace) -> None:
    """Per-category sensitivity analysis with BH-FDR correction."""
    from amplifier_research_block_hypothesis.domain import (
        compute_domain_sensitivity,
        domain_to_markdown,
    )

    results = _load_jsonl(args.results)
    items = _load_jsonl(args.items)

    sensitivity = compute_domain_sensitivity(
        results,
        items,
        baseline_approach=args.baseline_approach,
        treatment_approach=args.treatment_approach,
    )

    report = domain_to_markdown(sensitivity, output_path=args.output)

    if args.output:
        print(f"Domain sensitivity report written to: {args.output}")
    else:
        print(report)


# ─────────────────────────────────────────────────────────────────────────────
# Subcommand 4: block-evaluation-verdict
# ─────────────────────────────────────────────────────────────────────────────


def _load_splits_from_ablation_dir(
    ablation_dir: Path,
    baseline_condition: str,
    treatment_condition: str,
) -> list[dict]:
    """Load paired splits from subdirectories of ablation_dir.

    Each subdirectory is treated as one split.  Within each split dir,
    looks for ``{baseline_condition}.jsonl`` and ``{treatment_condition}.jsonl``.
    """
    from amplifier_research_block_hypothesis.ablation import _compute_pair_stats

    splits = []
    for split_dir in sorted(ablation_dir.iterdir()):
        if not split_dir.is_dir():
            continue
        baseline_file = split_dir / f"{baseline_condition}.jsonl"
        treatment_file = split_dir / f"{treatment_condition}.jsonl"
        if not baseline_file.exists() or not treatment_file.exists():
            continue
        b_recs = _load_jsonl(str(baseline_file))
        t_recs = _load_jsonl(str(treatment_file))
        stats = _compute_pair_stats(b_recs, t_recs)
        splits.append(
            {
                "n": stats["n_paired"],
                "n_01": stats["n_01"],
                "n_10": stats["n_10"],
            }
        )

    return splits


def _cmd_block_evaluation_verdict(args: argparse.Namespace) -> None:
    """Apply pre-registered thresholds and emit a JSON verdict."""
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    ablation_dir = Path(args.ablation_dir)
    if not ablation_dir.is_dir():
        raise FileNotFoundError(f"Ablation directory not found: {args.ablation_dir}")

    splits = _load_splits_from_ablation_dir(
        ablation_dir,
        baseline_condition=args.baseline_condition,
        treatment_condition=args.treatment_condition,
    )

    if not splits:
        print(
            f"Warning: no paired splits found in {ablation_dir} "
            f"(looked for {args.baseline_condition}.jsonl + {args.treatment_condition}.jsonl "
            "in each subdirectory).",
            file=sys.stderr,
        )

    result = compute_verdict(
        splits=splits,
        threshold_paired_delta=args.threshold_paired_delta,
        threshold_substantive_delta=args.threshold_substantive_delta,
        threshold_fdr=args.threshold_fdr,
        threshold_replication_splits=args.threshold_replication_splits,
    )

    json_text = json.dumps(result, indent=2)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_text, encoding="utf-8")
        print(f"Verdict written to: {args.output}")
    else:
        print(json_text)


# ─────────────────────────────────────────────────────────────────────────────
# Parser builder
# ─────────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="amplifier-research-block-hypothesis",
        description=(
            "Block hypothesis evaluation: per-rule firing analysis, "
            "ablation comparison, domain sensitivity, and pre-registered verdict."
        ),
    )
    root.set_defaults(func=None)
    subs = root.add_subparsers(dest="command", metavar="SUBCOMMAND")

    # ── analyze-rule-firing ───────────────────────────────────────────────
    arf = subs.add_parser(
        "analyze-rule-firing",
        help="Per-rule heuristic firing analysis against stage traces",
    )
    arf.add_argument("--block", required=True, metavar="PATH", help="Path to block JSON file")
    arf.add_argument("--traces", required=True, metavar="PATH", help="Path to stage_traces.jsonl")
    arf.add_argument(
        "--output", default=None, metavar="PATH", help="Output Markdown file (stdout if omitted)"
    )
    arf.set_defaults(func=_cmd_analyze_rule_firing)

    # ── ablation-summary ──────────────────────────────────────────────────
    abl = subs.add_parser(
        "ablation-summary",
        help="Multi-condition ablation comparison table",
    )
    abl.add_argument(
        "--conditions", required=True, metavar="C0,C3,...", help="Comma-separated condition names"
    )
    abl.add_argument(
        "--results-dir",
        required=True,
        metavar="PATH",
        help="Directory with {condition}.jsonl files",
    )
    abl.add_argument(
        "--output", default=None, metavar="PATH", help="Output Markdown file (stdout if omitted)"
    )
    abl.set_defaults(func=_cmd_ablation_summary)

    # ── domain-sensitivity ────────────────────────────────────────────────
    dom = subs.add_parser(
        "domain-sensitivity",
        help="Per-category sensitivity with BH-FDR correction",
    )
    dom.add_argument(
        "--results", required=True, metavar="PATH", help="Path to results.jsonl (all approaches)"
    )
    dom.add_argument(
        "--items", required=True, metavar="PATH", help="Path to items.jsonl (with category field)"
    )
    dom.add_argument(
        "--baseline-approach",
        default="A0",
        metavar="ID",
        help="Approach ID for baseline (default: A0)",
    )
    dom.add_argument(
        "--treatment-approach",
        default="A12",
        metavar="ID",
        help="Approach ID for treatment (default: A12)",
    )
    dom.add_argument(
        "--output", default=None, metavar="PATH", help="Output Markdown file (stdout if omitted)"
    )
    dom.set_defaults(func=_cmd_domain_sensitivity)

    # ── block-evaluation-verdict ──────────────────────────────────────────
    vrd = subs.add_parser(
        "block-evaluation-verdict",
        help="Apply pre-registered thresholds to yield a JSON verdict",
    )
    vrd.add_argument(
        "--ablation-dir",
        required=True,
        metavar="PATH",
        help="Directory with split subdirs, each containing {baseline}.jsonl and {treatment}.jsonl",
    )
    vrd.add_argument(
        "--baseline-condition",
        default="C0",
        metavar="NAME",
        help="Baseline condition filename stem (default: C0)",
    )
    vrd.add_argument(
        "--treatment-condition",
        default="treatment",
        metavar="NAME",
        help="Treatment condition filename stem (default: treatment)",
    )
    vrd.add_argument(
        "--threshold-paired-delta",
        type=float,
        default=5.0,
        metavar="PP",
        help="Minimum net delta pp for WORKS (default: 5.0)",
    )
    vrd.add_argument(
        "--threshold-substantive-delta",
        type=float,
        default=10.0,
        metavar="PP",
        help="Minimum substantive delta pp for WORKS (default: 10.0)",
    )
    vrd.add_argument(
        "--threshold-fdr",
        type=float,
        default=0.05,
        metavar="Q",
        help="Maximum McNemar p for WORKS (default: 0.05)",
    )
    vrd.add_argument(
        "--threshold-replication-splits",
        type=int,
        default=3,
        metavar="N",
        help="Minimum positive splits for WORKS (default: 3)",
    )
    vrd.add_argument(
        "--output", default=None, metavar="PATH", help="Output JSON file (stdout if omitted)"
    )
    vrd.set_defaults(func=_cmd_block_evaluation_verdict)

    return root


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point for ``amplifier-research-block-hypothesis``."""
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
