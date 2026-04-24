"""
amplifier_research_resume — Experiment Resume/Repair capability.

Provides plan / subset / merge operations for resuming aborted experiment
runs.  When a sweep aborts mid-run, this tool helps identify which items have
clean records (preserve), which need re-running (errored or never-started),
and merges the preserved + new records into a unified result.

Quick start::

    from pathlib import Path
    from amplifier_research_resume.plan import categorize_records

    manifest = categorize_records(
        partial_results=Path("experiments/foo/results.jsonl.partial"),
        full_input=Path("data/reserved/dev.jsonl"),
        approaches=["A0", "A4"],
    )
    manifest.save(Path("experiments/foo/resume_manifest.json"))
    print(manifest.totals)
"""

from .manifest import ResumeManifest
from .merge import MergeSummary, merge_results
from .mount import mount
from .plan import categorize_records
from .subset import write_subset

__version__ = "0.1.0"

__all__ = [
    "categorize_records",
    "ResumeManifest",
    "write_subset",
    "merge_results",
    "MergeSummary",
    "mount",
]
