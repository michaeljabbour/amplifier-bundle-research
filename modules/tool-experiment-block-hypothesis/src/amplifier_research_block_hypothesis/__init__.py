"""
amplifier_research_block_hypothesis — Block hypothesis evaluation toolkit.

Scientific rigour for persistent reflection blocks: per-rule firing analysis,
multi-condition ablation comparison, per-domain sensitivity, and pre-registered
verdict computation.

Quick start::

    from amplifier_research_block_hypothesis.rule_firing import analyze_rule_firing
    from amplifier_research_block_hypothesis.ablation import compute_ablation_summary
    from amplifier_research_block_hypothesis.domain import compute_domain_sensitivity
    from amplifier_research_block_hypothesis.verdict import compute_verdict

    block = json.loads(Path("hle_handcrafted.json").read_text())
    traces = [json.loads(l) for l in Path("stage_traces.jsonl").read_text().splitlines() if l]
    analysis = analyze_rule_firing(block, traces)
"""

from .mount import mount

__version__ = "0.1.0"

__all__ = ["mount", "__version__"]
