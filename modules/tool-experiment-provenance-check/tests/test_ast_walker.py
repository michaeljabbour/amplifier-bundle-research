"""
TDD RED phase — test_ast_walker.py

Tests for ast_walker.py: parse Python source code for file path references.
These tests import from amplifier_research_provenance_check.ast_walker,
which does NOT exist yet.  All tests must FAIL on first run.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_finds_string_literals_with_data_prefix() -> None:
    """String literal 'data/foo.json' is returned by the walker."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
import json

with open("data/foo.json") as f:
    data = json.load(f)
"""
    paths = walk_script(source)
    assert "data/foo.json" in paths, f"Expected 'data/foo.json' in paths, got: {paths}"


def test_finds_path_constructions() -> None:
    """Path('data') / 'foo.json' is resolved to 'data/foo.json'."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
from pathlib import Path

data_file = Path("data") / "foo.json"
"""
    paths = walk_script(source)
    assert "data/foo.json" in paths, f"Expected 'data/foo.json' in paths, got: {paths}"


def test_finds_module_level_constants() -> None:
    """Module-level constant _DATA_PATH = Path('data/x') is detected."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
from pathlib import Path

_DATA_PATH = Path("data/x")

def load():
    return open(_DATA_PATH)
"""
    paths = walk_script(source)
    assert "data/x" in paths, f"Expected 'data/x' in paths, got: {paths}"


def test_ignores_non_data_strings() -> None:
    """Strings without data prefixes (e.g. 'hello') are not returned."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
print("hello")
name = "world"
x = "foo/bar"
"""
    paths = walk_script(source)
    assert "hello" not in paths
    assert "world" not in paths
    assert "foo/bar" not in paths


def test_handles_nested_paths() -> None:
    """Path('data') / 'subdir' / 'file.json' resolves to 'data/subdir/file.json'."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
from pathlib import Path

nested = Path("data") / "subdir" / "file.json"
"""
    paths = walk_script(source)
    assert "data/subdir/file.json" in paths, (
        f"Expected 'data/subdir/file.json' in paths, got: {paths}"
    )


def test_normalizes_paths() -> None:
    """'./data/foo' and 'data/foo' both normalize to 'data/foo' (no duplicates)."""
    from amplifier_research_provenance_check.ast_walker import walk_script

    source = """
path1 = "./data/foo"
path2 = "data/foo"
"""
    paths = walk_script(source)
    assert "data/foo" in paths, f"Expected 'data/foo' in paths, got: {paths}"
    assert paths.count("data/foo") == 1, (
        f"Expected 'data/foo' exactly once, got {paths.count('data/foo')} times in: {paths}"
    )
