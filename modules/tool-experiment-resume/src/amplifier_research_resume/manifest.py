"""
manifest.py — ResumeManifest dataclass + JSON serialization.

The manifest is the central artifact produced by ``plan`` and consumed by
``subset`` and ``merge``.  It records which items are clean, which need
re-running, and what the expected totals are.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ResumeManifest:
    """Complete description of a resume plan for one experiment run.

    Attributes:
        version: Schema version string (currently ``"1.0"``).
        generated_at: ISO-8601 timestamp of when the manifest was created.
        source_partial: Path to the original partial results file.
        source_full_input: Path to the original full-input jsonl.
        approaches: List of approach IDs that were running (e.g. ``["A0", "A4"]``).
        categorization: Dict with three keys:

            - ``clean_complete_items``: list of item IDs ready to preserve.
            - ``errored_items``: list of ``{item_id, errored_approaches, reason}``.
            - ``never_started_items``: list of item IDs not in partial at all.

        totals: Aggregate counts (clean, errored, never_started, rerun, expected).
    """

    version: str
    source_partial: str
    source_full_input: str
    approaches: list[str]
    categorization: dict[str, Any]
    totals: dict[str, int]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serialisable dict."""
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "source_partial": self.source_partial,
            "source_full_input": self.source_full_input,
            "approaches": self.approaches,
            "categorization": self.categorization,
            "totals": self.totals,
        }

    def save(self, path: Path) -> None:
        """Write manifest to *path* as pretty-printed JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ResumeManifest":
        """Load a manifest from a JSON file produced by :meth:`save`."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            version=data["version"],
            generated_at=data.get("generated_at", ""),
            source_partial=data["source_partial"],
            source_full_input=data["source_full_input"],
            approaches=data["approaches"],
            categorization=data["categorization"],
            totals=data["totals"],
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def rerun_item_ids(self) -> list[str]:
        """Return all item IDs that need re-running (errored ∪ never_started)."""
        errored = [e["item_id"] for e in self.categorization.get("errored_items", [])]
        never_started = self.categorization.get("never_started_items", [])
        return errored + never_started
