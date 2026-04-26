"""
cli.py — amplifier-research-provenance-check command-line interface.

Subcommands:
  audit-script         --script PATH --repo PATH [--output PATH]
  check-files          --files FILE [FILE ...] --repo PATH
  pre-experiment-gate  --script PATH --repo PATH
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# audit-script subcommand
# ---------------------------------------------------------------------------


def _cmd_audit_script(args: argparse.Namespace) -> None:
    """
    Full pipeline: parse script → check all discovered files → write Markdown report.

    Exit codes:
      0 — report written (even if UNTRACKED files found; report is the artifact)
    """
    from amplifier_research_provenance_check.ast_walker import walk_script
    from amplifier_research_provenance_check.git_check import check_files
    from amplifier_research_provenance_check.report import generate_report

    script_path = Path(args.script)
    repo_path = Path(args.repo).resolve()

    source = script_path.read_text(encoding="utf-8")
    discovered = walk_script(source)

    results = check_files(discovered, repo_path)

    report_text = generate_report(
        results,
        script_path=str(script_path),
        repo_path=str(repo_path),
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report_text, encoding="utf-8")
        print(f"Provenance report written to: {args.output}")
    else:
        print(report_text)


# ---------------------------------------------------------------------------
# check-files subcommand
# ---------------------------------------------------------------------------


def _cmd_check_files(args: argparse.Namespace) -> None:
    """
    Lightweight check of explicitly listed files.

    Exit codes:
      0 — all TRACKED
      1 — any UNTRACKED
      2 — any MISSING (no UNTRACKED present)
    """
    from amplifier_research_provenance_check.git_check import FileStatus, check_files

    repo_path = Path(args.repo).resolve()
    results = check_files(list(args.files), repo_path)

    for path, status in sorted(results.items()):
        print(f"  {status.value:<14}  {path}")

    has_untracked = any(s == FileStatus.UNTRACKED for s in results.values())
    has_missing = any(s == FileStatus.MISSING for s in results.values())

    if has_untracked:
        print(
            f"\nResult: {sum(s == FileStatus.UNTRACKED for s in results.values())}"
            " UNTRACKED file(s) found.",
            file=sys.stderr,
        )
        sys.exit(1)
    if has_missing:
        print(
            f"\nResult: {sum(s == FileStatus.MISSING for s in results.values())}"
            " MISSING file(s) found.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"\nResult: all {len(results)} file(s) are TRACKED.")


# ---------------------------------------------------------------------------
# pre-experiment-gate subcommand
# ---------------------------------------------------------------------------


def _cmd_pre_experiment_gate(args: argparse.Namespace) -> None:
    """
    Hard gate: parse script, check all discovered files, exit non-zero if any UNTRACKED.

    Designed for shell wrappers that launch experiments — refuses to launch
    with untracked artifacts.

    Exit codes:
      0 — all files tracked (gate PASSED)
      1 — untracked or missing files found (gate FAILED)
    """
    from amplifier_research_provenance_check.ast_walker import walk_script
    from amplifier_research_provenance_check.git_check import FileStatus, check_files

    script_path = Path(args.script)
    repo_path = Path(args.repo).resolve()

    source = script_path.read_text(encoding="utf-8")
    discovered = walk_script(source)
    results = check_files(discovered, repo_path)

    n_untracked = sum(s == FileStatus.UNTRACKED for s in results.values())
    n_missing = sum(s == FileStatus.MISSING for s in results.values())
    n_tracked = sum(s == FileStatus.TRACKED for s in results.values())
    n_total = len(results)

    # Minimal summary
    print(
        f"Provenance gate: {n_tracked} TRACKED, "
        f"{n_untracked} UNTRACKED, "
        f"{n_missing} MISSING  ({n_total} files checked)"
    )

    if n_untracked > 0 or n_missing > 0:
        print("")
        for path, status in sorted(results.items()):
            if status in (FileStatus.UNTRACKED, FileStatus.MISSING):
                print(f"  [{status.value}]  {path}")
        print(
            "\nGate FAILED — commit untracked/missing files before running the experiment.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nGate PASSED — all data files are tracked.")


# ---------------------------------------------------------------------------
# Parser builder
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="amplifier-research-provenance-check",
        description=(
            "Pre-experiment data provenance checker. "
            "Audits that all data files referenced by a script are git-tracked."
        ),
    )
    root.set_defaults(func=None)
    subs = root.add_subparsers(dest="command", metavar="SUBCOMMAND")

    # --- audit-script ---
    audit = subs.add_parser(
        "audit-script",
        help="Parse script, check all discovered data files, write Markdown report",
    )
    audit.add_argument(
        "--script",
        required=True,
        metavar="PATH",
        help="Path to the Python script to audit",
    )
    audit.add_argument(
        "--repo",
        required=True,
        metavar="PATH",
        help="Root of the git repository",
    )
    audit.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Output path for Markdown report (prints to stdout if omitted)",
    )
    audit.set_defaults(func=_cmd_audit_script)

    # --- check-files ---
    chk = subs.add_parser(
        "check-files",
        help=("Check listed files directly. Exit 0=all tracked, 1=any untracked, 2=any missing"),
    )
    chk.add_argument(
        "--files",
        nargs="+",
        required=True,
        metavar="FILE",
        help="One or more file paths to check",
    )
    chk.add_argument(
        "--repo",
        required=True,
        metavar="PATH",
        help="Root of the git repository",
    )
    chk.set_defaults(func=_cmd_check_files)

    # --- pre-experiment-gate ---
    gate = subs.add_parser(
        "pre-experiment-gate",
        help=(
            "Hard gate: parse script, exit non-zero if ANY untracked file found. "
            "Use in shell wrappers before launching experiments."
        ),
    )
    gate.add_argument(
        "--script",
        required=True,
        metavar="PATH",
        help="Path to the Python script to gate",
    )
    gate.add_argument(
        "--repo",
        required=True,
        metavar="PATH",
        help="Root of the git repository",
    )
    gate.set_defaults(func=_cmd_pre_experiment_gate)

    return root


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for ``amplifier-research-provenance-check``."""
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
