"""
TDD RED phase — test_git_check.py

Tests for git_check.py: check whether files are git-tracked.
These tests import from amplifier_research_provenance_check.git_check,
which does NOT exist yet.  All tests must FAIL on first run.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _init_repo(path: Path) -> None:
    """Initialize a git repo with a baseline commit."""
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    (path / ".gitkeep").write_text("")
    subprocess.run(["git", "add", ".gitkeep"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_detects_tracked_file(tmp_path: Path) -> None:
    """A committed file is classified as TRACKED."""
    from amplifier_research_provenance_check.git_check import FileStatus, check_file

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "foo.txt").write_text("hello")
    subprocess.run(["git", "add", "foo.txt"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add foo"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )

    result = check_file("foo.txt", repo)
    assert result == FileStatus.TRACKED, f"Expected TRACKED, got {result}"


def test_detects_untracked_file(tmp_path: Path) -> None:
    """A file that exists but is not added to git is classified as UNTRACKED."""
    from amplifier_research_provenance_check.git_check import FileStatus, check_file

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "bar.txt").write_text("untracked content")

    result = check_file("bar.txt", repo)
    assert result == FileStatus.UNTRACKED, f"Expected UNTRACKED, got {result}"


def test_detects_missing_file(tmp_path: Path) -> None:
    """A file path that does not exist on disk is classified as MISSING."""
    from amplifier_research_provenance_check.git_check import FileStatus, check_file

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    result = check_file("nonexistent.txt", repo)
    assert result == FileStatus.MISSING, f"Expected MISSING, got {result}"


def test_detects_gitignored_file(tmp_path: Path) -> None:
    """A file that matches .gitignore is classified as IN_GITIGNORE."""
    from amplifier_research_provenance_check.git_check import FileStatus, check_file

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    # Add a .gitignore that ignores the test file
    (repo / ".gitignore").write_text("ignored.txt\n")
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add gitignore"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )

    # Create the ignored file (exists on disk, but gitignored)
    (repo / "ignored.txt").write_text("ignored content")

    result = check_file("ignored.txt", repo)
    assert result == FileStatus.IN_GITIGNORE, f"Expected IN_GITIGNORE, got {result}"


def test_handles_outside_repo(tmp_path: Path) -> None:
    """A file whose absolute path is outside the repo returns OUTSIDE_REPO."""
    from amplifier_research_provenance_check.git_check import FileStatus, check_file

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    # File exists on disk but is outside the repo directory
    outside_file = tmp_path / "outside_file.txt"
    outside_file.write_text("outside content")

    result = check_file(str(outside_file), repo)
    assert result == FileStatus.OUTSIDE_REPO, f"Expected OUTSIDE_REPO, got {result}"
