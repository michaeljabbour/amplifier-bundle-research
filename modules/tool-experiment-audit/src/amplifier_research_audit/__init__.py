"""
amplifier_research_audit — Experiment Integrity Audit capability.

Reusable tool for auditing experiment directories against a configurable
integrity contract.  Detects HANDLER_ERROR cascades, response-quality issues,
judge-coverage gaps, missing manifests, and implausible statistics before any
downstream analysis trusts the numbers.

Quick start::

    from amplifier_research_audit import audit_experiment
    result = audit_experiment(Path("experiments/production/a12a_v2"))
    print(result.verdict)  # PASS | FAIL | SUSPICIOUS
"""

from .audit import AuditResult, Verdict, audit_experiment
from .checklist import CheckResult, CheckStatus, IntegrityContract
from .report import generate_batch_report, generate_report

__version__ = "0.1.0"

__all__ = [
    "audit_experiment",
    "AuditResult",
    "Verdict",
    "CheckResult",
    "CheckStatus",
    "IntegrityContract",
    "generate_report",
    "generate_batch_report",
]
