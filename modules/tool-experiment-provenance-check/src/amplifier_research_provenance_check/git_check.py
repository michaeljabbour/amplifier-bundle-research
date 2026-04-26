"""
git_check.py — Check whether files are git-tracked.

Uses ``git ls-files --error-unmatch`` (tracked check) and
``git check-ignore -q`` (gitignore check) to classify each file.
"""

from __future__ import annotations

import subprocess
from enum import Enum
from pathlib import Path


class FileStatus(str, Enum):
    """Classification of a file's git-tracking status."""

    TRACKED = "TRACKED"
    UNTRACKED = "UNTRACKED"
    MISSING = "MISSING"
    IN_GITIGNORE = "IN_GITIGNORE"
    OUTSIDE_REPO = "OUTSIDE_REPO"


def check_file(
    path: str | Path,
    repo: str | Path,
) -> FileStatus:
    """
    Check the git-tracking status of a single file.

    Parameters
    ----------
    path:
        File path to check — may be relative (resolved against *repo*) or absolute.
    repo:
        Root of the git repository.

    Returns
    -------
    FileStatus
        TRACKED, UNTRACKED, MISSING, IN_GITIGNORE, or OUTSIDE_REPO.
    """
    repo_root = Path(repo).resolve()
    raw = Path(path)

    # --- resolve absolute path and relative-to-repo path ---
    if raw.is_absolute():
        abs_path = raw
        try:
            rel_path = abs_path.relative_to(repo_root)
        except ValueError:
            return FileStatus.OUTSIDE_REPO
    else:
        rel_path = raw
        abs_path = repo_root / raw

    # --- existence check ---
    if not abs_path.exists():
        return FileStatus.MISSING

    # --- git-tracked check ---
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(rel_path)],
        capture_output=True,
        cwd=str(repo_root),
    )
    if result.returncode == 0:
        return FileStatus.TRACKED

    # --- gitignore check ---
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(rel_path)],
        capture_output=True,
        cwd=str(repo_root),
    )
    if result.returncode == 0:
        return FileStatus.IN_GITIGNORE

    return FileStatus.UNTRACKED


def check_files(
    paths: list[str],
    repo: str | Path,
) -> dict[str, FileStatus]:
    """
    Check the git-tracking status of multiple files.

    Parameters
    ----------
    paths:
        List of file paths (relative to *repo* or absolute).
    repo:
        Root of the git repository.

    Returns
    -------
    dict mapping each path string to its ``FileStatus``.
    """
    return {p: check_file(p, repo) for p in paths}
