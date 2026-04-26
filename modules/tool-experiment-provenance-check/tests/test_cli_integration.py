"""
TDD RED phase — test_cli_integration.py

End-to-end CLI integration tests for amplifier-research-provenance-check.
Invokes the CLI as a Python module so it works before the entry-point is
installed.  All tests must FAIL on first run (module not yet implemented).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI as a module so it works even before the entry-point is installed."""
    return subprocess.run(
        [sys.executable, "-m", "amplifier_research_provenance_check.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )


def _make_git_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo with a baseline commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    (repo / "README.md").write_text("test repo")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return repo


def _add_tracked_file(repo: Path, rel_path: str, content: str = "{}") -> Path:
    """Create a file and commit it so it is git-tracked."""
    full = repo / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content)
    subprocess.run(["git", "add", rel_path], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {rel_path}"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return full


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_audit_script_subcommand_runs(tmp_path: Path) -> None:
    """audit-script subcommand writes a report file and exits 0."""
    repo = _make_git_repo(tmp_path)
    _add_tracked_file(repo, "data/tracked.json")

    script = repo / "experiment.py"
    script.write_text('open("data/tracked.json")\n')

    output_file = tmp_path / "report.md"
    result = _run(
        "audit-script",
        "--script", str(script),
        "--repo", str(repo),
        "--output", str(output_file),
    )

    assert result.returncode == 0, (
        f"audit-script exited {result.returncode}:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert output_file.exists(), f"Expected report at {output_file}"
    content = output_file.read_text()
    assert "TRACKED" in content, f"Expected 'TRACKED' in report, got:\n{content[:600]}"


def test_check_files_returns_zero_when_all_tracked(tmp_path: Path) -> None:
    """check-files exits 0 when all specified files are git-tracked."""
    repo = _make_git_repo(tmp_path)
    _add_tracked_file(repo, "data/file_a.json")
    _add_tracked_file(repo, "data/file_b.jsonl")

    result = _run(
        "check-files",
        "--files", "data/file_a.json", "data/file_b.jsonl",
        "--repo", str(repo),
    )
    assert result.returncode == 0, (
        f"Expected exit code 0 (all tracked), got {result.returncode}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_check_files_returns_one_when_untracked(tmp_path: Path) -> None:
    """check-files exits 1 when at least one file is untracked."""
    repo = _make_git_repo(tmp_path)
    _add_tracked_file(repo, "data/tracked.json")

    # Create an untracked file (exists but not committed)
    untracked = repo / "data" / "untracked.json"
    untracked.write_text("{}")

    result = _run(
        "check-files",
        "--files", "data/tracked.json", "data/untracked.json",
        "--repo", str(repo),
    )
    assert result.returncode == 1, (
        f"Expected exit code 1 (untracked found), got {result.returncode}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_pre_experiment_gate_blocks_on_untracked(tmp_path: Path) -> None:
    """pre-experiment-gate exits non-zero when untracked files found in script."""
    repo = _make_git_repo(tmp_path)
    _add_tracked_file(repo, "data/tracked.json")

    # Create untracked file
    untracked = repo / "data" / "untracked.json"
    untracked.write_text("{}")

    script = repo / "run.py"
    script.write_text(
        'open("data/tracked.json")\nopen("data/untracked.json")\n'
    )

    result = _run(
        "pre-experiment-gate",
        "--script", str(script),
        "--repo", str(repo),
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit from gate (untracked file), got {result.returncode}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_end_to_end_catches_untracked_artifact(tmp_path: Path) -> None:
    """End-to-end: script with known-untracked artifact is flagged in the report."""
    repo = _make_git_repo(tmp_path)
    _add_tracked_file(repo, "data/tracked_reference.json")

    # Create the untracked artifact (the scenario we want to detect)
    untracked = repo / "data" / "persistent_blocks" / "important_data.json"
    untracked.parent.mkdir(parents=True, exist_ok=True)
    untracked.write_text('{"key": "value"}')

    # Script that references both files
    script = repo / "sweep.py"
    script.write_text(
        'import json\n'
        'ref = open("data/tracked_reference.json")\n'
        'critical = open("data/persistent_blocks/important_data.json")\n'
    )

    output_file = tmp_path / "provenance_report.md"
    result = _run(
        "audit-script",
        "--script", str(script),
        "--repo", str(repo),
        "--output", str(output_file),
    )

    assert result.returncode == 0, f"audit-script failed: {result.stderr}"
    assert output_file.exists()

    content = output_file.read_text()
    # The untracked file must appear in the report
    assert "important_data.json" in content, (
        f"Expected 'important_data.json' in report, got:\n{content[:800]}"
    )
    # And must be labeled UNTRACKED
    assert "UNTRACKED" in content, (
        f"Expected 'UNTRACKED' status in report, got:\n{content[:800]}"
    )
