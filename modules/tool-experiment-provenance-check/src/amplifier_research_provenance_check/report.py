"""
report.py — Generate Markdown provenance reports.

Summarizes the git-tracking status of all data files referenced by a script,
highlights UNTRACKED integrity gaps, lists MISSING files, and emits
actionable ``git add`` recommendations.
"""

from __future__ import annotations

from datetime import datetime, timezone

from amplifier_research_provenance_check.git_check import FileStatus


def generate_report(
    results: dict[str, FileStatus],
    script_path: str | None = None,
    repo_path: str | None = None,
) -> str:
    """
    Generate a Markdown provenance report.

    Parameters
    ----------
    results:
        Mapping of file path → ``FileStatus`` (from ``check_files``).
    script_path:
        Optional path to the script that was scanned (shown in header).
    repo_path:
        Optional repo root path (shown in header).

    Returns
    -------
    str
        Full Markdown report text.
    """
    # --- count by status ---
    counts: dict[FileStatus, int] = {s: 0 for s in FileStatus}
    for status in results.values():
        counts[status] += 1

    untracked = sorted(p for p, s in results.items() if s == FileStatus.UNTRACKED)
    missing = sorted(p for p, s in results.items() if s == FileStatus.MISSING)
    gitignored = sorted(p for p, s in results.items() if s == FileStatus.IN_GITIGNORE)
    outside = sorted(p for p, s in results.items() if s == FileStatus.OUTSIDE_REPO)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines: list[str] = []

    # ---- header ----
    lines.append("# Provenance Check Report")
    lines.append("")
    if script_path:
        lines.append(f"**Script:** `{script_path}`")
    if repo_path:
        lines.append(f"**Repo:** `{repo_path}`")
    lines.append(f"**Generated:** {now}")
    lines.append("")

    # ---- summary table ----
    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| TRACKED | {counts[FileStatus.TRACKED]} |")
    lines.append(f"| UNTRACKED | {counts[FileStatus.UNTRACKED]} |")
    lines.append(f"| MISSING | {counts[FileStatus.MISSING]} |")
    lines.append(f"| IN_GITIGNORE | {counts[FileStatus.IN_GITIGNORE]} |")
    if counts[FileStatus.OUTSIDE_REPO]:
        lines.append(f"| OUTSIDE_REPO | {counts[FileStatus.OUTSIDE_REPO]} |")
    lines.append("")

    # ---- all files (detailed) ----
    if results:
        lines.append("## All Referenced Files")
        lines.append("")
        lines.append("| File | Status |")
        lines.append("|------|--------|")
        for path, status in sorted(results.items()):
            lines.append(f"| `{path}` | {status.value} |")
        lines.append("")

    # ---- integrity gaps ----
    lines.append("## Integrity Gaps — UNTRACKED Files")
    lines.append("")
    if untracked:
        lines.append(
            "These files are referenced by the script but are **NOT git-tracked**. "
            "They will not be available to anyone who clones the repository."
        )
        lines.append("")
        for path in untracked:
            lines.append(f"- `{path}`")
    else:
        lines.append("_(none — all referenced files are tracked or otherwise accounted for)_")
    lines.append("")

    # ---- missing files ----
    lines.append("## Missing Files")
    lines.append("")
    if missing:
        lines.append(
            "These files are referenced by the script but do **NOT exist on disk**. "
            "This may indicate stale references or a broken environment."
        )
        lines.append("")
        for path in missing:
            lines.append(f"- `{path}`")
    else:
        lines.append("_(none)_")
    lines.append("")

    # ---- gitignored (informational) ----
    if gitignored:
        lines.append("## Gitignored Files (Informational)")
        lines.append("")
        lines.append(
            "These files exist on disk but match `.gitignore`. "
            "They are intentionally excluded from version control."
        )
        lines.append("")
        for path in gitignored:
            lines.append(f"- `{path}`")
        lines.append("")

    # ---- outside repo (informational) ----
    if outside:
        lines.append("## Outside-Repo References (Informational)")
        lines.append("")
        lines.append("These absolute paths resolve outside the repository root (not checkable):")
        lines.append("")
        for path in outside:
            lines.append(f"- `{path}`")
        lines.append("")

    # ---- recommendations ----
    lines.append("## Recommendations")
    lines.append("")
    if untracked:
        lines.append(
            "The following files **must be committed** to git before this experiment "
            "can be reproduced by others:"
        )
        lines.append("")
        lines.append("```bash")
        for path in untracked:
            lines.append(f"git add {path}")
        lines.append('git commit -m "feat(data): track experiment data files for reproducibility"')
        lines.append("```")
        lines.append("")
        lines.append(
            "> **Why this matters:** untracked data files created the reproducibility gap "
            "discovered in commit `e189188` (hle_handcrafted.json). "
            "This tool exists to catch such gaps automatically."
        )
    else:
        lines.append(
            "All referenced data files are tracked or otherwise accounted for. No action needed."
        )
    lines.append("")

    return "\n".join(lines)
