"""
amplifier_research_stage_analyzer — Stage-trace empty-response root-cause analyzer.

Ingests ``stage_traces.jsonl`` (generator / critic / revert_decision records),
categorizes empty-final records by failure-mode origin, and applies
pre-registered H1a/H1b confirmation criteria.

Quick start::

    from amplifier_research_stage_analyzer.ingest import ingest_stage_traces
    from amplifier_research_stage_analyzer.categorize import categorize_empty
    from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
    from amplifier_research_stage_analyzer.report import generate_report

    records = ingest_stage_traces("experiments/foo/stage_traces.jsonl")
    cat = categorize_empty(records)
    hyp = test_h1_hypotheses(cat)
    md = generate_report({"categorize": cat, "hypothesis": hyp,
                           "total_records": len(records),
                           "total_empty": sum(cat["counts"].values())})
"""

from .mount import mount

__version__ = "0.1.0"

__all__ = ["mount", "__version__"]
