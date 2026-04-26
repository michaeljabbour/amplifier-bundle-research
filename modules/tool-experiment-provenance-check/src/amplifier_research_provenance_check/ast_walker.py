"""
ast_walker.py — Parse Python source code for file path references.

Finds all data-file path references using three complementary strategies:

1. **String literals**: ``open("data/foo.json")`` — caught by ``visit_Constant``.
2. **Path constructions**: ``Path("data/foo.json")`` or ``Path("data") / "foo.json"``
   — caught by ``visit_BinOp`` / ``_extract_div_chain``.
3. **Variable-base chains**: ``_ROOT / "data" / "sub" / "file.jsonl"`` — caught by
   ``_collect_right_suffix_paths``, which extracts the longest data-prefixed right
   suffix even when the leftmost base is a non-constant variable.
"""

from __future__ import annotations

import ast
from pathlib import PurePosixPath

# ---------------------------------------------------------------------------
# Data-path prefixes to watch for
# ---------------------------------------------------------------------------

DATA_PREFIXES: tuple[str, ...] = (
    "data/",
    "experiments/",
    "configs/",
    "inputs/",
    "outputs/",
    "results/",
    "models/",
    "checkpoints/",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(path: str) -> str:
    """Normalize a path: strip leading ./ and collapse redundant separators."""
    try:
        return str(PurePosixPath(path))
    except Exception:
        return path


def _has_data_prefix(path: str) -> bool:
    """Return True if *path* (after normalization) starts with a known data prefix."""
    normalized = _normalize(path)
    for prefix in DATA_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) > len(prefix):
            return True
    return False


def _is_path_call(node: ast.expr) -> bool:
    """Return True if *node* is a call to ``Path(...)``."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "Path"
    if isinstance(func, ast.Attribute):
        return func.attr == "Path"
    return False


def _extract_div_chain(node: ast.expr) -> str | None:
    """
    Try to extract a single path string from a fully-static ``/``-chain.

    Returns a path string if the entire expression is resolvable to a constant,
    or ``None`` if any part involves a variable or other non-constant.

    Examples::

        Path("data") / "foo"       → "data/foo"
        Path("data") / "a" / "b"  → "data/a/b"
        Path("data/foo.json")      → "data/foo.json"
        Constant("data/foo")       → "data/foo"
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if _is_path_call(node):
        assert isinstance(node, ast.Call)
        if node.args and isinstance(node.args[0], ast.Constant):
            val = node.args[0].value
            if isinstance(val, str):
                return val
        return None

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _extract_div_chain(node.left)
        if left is None:
            return None
        right = _extract_div_chain(node.right)
        if right is None:
            return None
        return str(PurePosixPath(left) / right)

    return None


def _collect_right_suffix_paths(node: ast.expr) -> list[str]:
    """
    Collect all right-suffix path strings from a ``/``-chain.

    Used when the leftmost element of a chain is a variable (e.g., ``_ROOT / "data" / ...``).
    Returns all right-side sub-paths, from shortest to longest, so the caller can
    select the longest data-prefixed entry.

    Example — ``_ROOT / "data" / "sub" / "file.json"`` returns::

        ["file.json", "sub/file.json", "data/sub/file.json"]
    """
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
        # Leaf: try to extract as a constant
        val = _extract_div_chain(node)
        return [val] if val is not None else []

    right_val = _extract_div_chain(node.right)
    if right_val is None:
        return []

    left_suffixes = _collect_right_suffix_paths(node.left)

    # Build new suffixes: prepend each left suffix with right_val
    result: list[str] = [right_val]  # right alone
    for s in left_suffixes:
        result.append(str(PurePosixPath(s) / right_val))
    return result


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class _PathWalker(ast.NodeVisitor):
    """Walk an AST and collect all data-file path references."""

    def __init__(self) -> None:
        self._paths: list[str] = []
        self._seen: set[str] = set()

    def _add(self, raw: str) -> None:
        normalized = _normalize(raw)
        if normalized not in self._seen:
            self._seen.add(normalized)
            self._paths.append(normalized)

    def visit_Constant(self, node: ast.Constant) -> None:  # noqa: N802
        """Catch plain string literals: ``'data/foo.json'``."""
        if isinstance(node.value, str) and _has_data_prefix(node.value):
            self._add(node.value)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:  # noqa: N802
        """Catch ``Path(...) / '...' / '...'`` chains."""
        if isinstance(node.op, ast.Div):
            # Strategy 1: fully-static chain (Path("data") / "sub" / "file")
            path = _extract_div_chain(node)
            if path is not None:
                if _has_data_prefix(path):
                    self._add(path)
                return  # full chain resolved — don't recurse into children

            # Strategy 2: variable-base chain (_ROOT / "data" / "sub" / "file")
            suffixes = _collect_right_suffix_paths(node)
            data_suffixes = [s for s in suffixes if _has_data_prefix(s)]
            if data_suffixes:
                # Add the longest (most specific) data-prefixed suffix
                self._add(max(data_suffixes, key=len))
                return  # found a path in this chain — don't recurse

        self.generic_visit(node)

    @property
    def paths(self) -> list[str]:
        return list(self._paths)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def walk_script(source: str) -> list[str]:
    """
    Parse Python *source* and return a deduplicated list of data-file path references.

    Detects:
    - String literals: ``'data/foo.json'``
    - ``Path(...)`` constructions: ``Path("data/foo.json")``
    - ``/``-chains: ``Path("data") / "sub" / "file.json"``
    - Variable-base chains: ``_ROOT / "data" / "reserved" / "file.jsonl"``

    All returned paths are normalized (``./`` stripped, forward slashes).
    """
    tree = ast.parse(source)
    walker = _PathWalker()
    walker.visit(tree)
    return walker.paths
