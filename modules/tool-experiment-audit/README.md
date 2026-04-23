# tool-experiment-audit

Experiment integrity audit capability for the Amplifier research bundle.  Audits
any experiment directory for a class of pipeline-failure problems where
`[HANDLER_ERROR]` placeholder records are disguised as plausible results.

Run this **before trusting any experiment's numbers**.

---

## Quick start

```bash
# Single experiment
python -m amplifier_research_audit \
    --experiment experiments/production/a12a_v2 \
    --expected-items 300 \
    --output audit_reports/a12a_v2_audit.md

# Batch — audit every results.jsonl under a root
python -m amplifier_research_audit \
    --experiments-root experiments/ \
    --output audit_reports/full_audit.md
```

---

## The integrity contract

Ten checks across five categories:

| # | Check | Fails when |
|---|-------|-----------|
| 1 | `check_row_count` | Actual rows ≠ expected N × approaches |
| 2 | `check_handler_error_rate` | `[HANDLER_ERROR]` / `[ITEM_TIMEOUT]` > 5% |
| 3 | `check_response_length_distribution` | Median < 100 chars OR > 5% "short" |
| 4 | `check_no_duplicate_responses` | > 10% identical responses (stuck generator) |
| 5 | `check_judge_coverage` | Any record missing `correct_by_judge` |
| 6 | `check_judge_distribution` | Overall accuracy < 1% (suspicious) → WARN |
| 7 | `check_manifest_present` | No `manifest.json` / `experiment_meta.json` → WARN |
| 8 | `check_manifest_fields` | Required fields missing from manifest |
| 9 | `check_baseline_plausibility` | C0 accuracy outside [1%, 25%] → WARN |
| 10 | `check_help_hurt_ratio_reasonable` | Ratio outside [0.2, 5.0] → WARN |

**Verdict logic:**
- Any ❌ FAIL → overall **FAIL**
- Any ⚠️ WARN (no FAIL) → overall **SUSPICIOUS**
- All ✅ / ⏭️ → overall **PASS**

---

## Installation

```bash
# From the research bundle root:
pip install -e modules/tool-experiment-audit/

# Or from the module directory:
cd modules/tool-experiment-audit
pip install -e .
```

---

## Python API

```python
from pathlib import Path
from amplifier_research_audit import audit_experiment, generate_report

result = audit_experiment(Path("experiments/production/a12a_v2"))
print(result.verdict)          # PASS | FAIL | SUSPICIOUS
print(result.handler_error_rate)  # e.g. 0.27

report_md = generate_report(result)
Path("audit.md").write_text(report_md)
```

Customise thresholds via `IntegrityContract`:

```python
from amplifier_research_audit import audit_experiment, IntegrityContract

contract = IntegrityContract(
    handler_error_threshold=0.02,   # tighter: 2% max
    baseline_expected_range=(0.01, 0.30),
)
result = audit_experiment(Path("exp/"), contract=contract)
```

---

## Module structure

```
modules/tool-experiment-audit/
├── src/amplifier_research_audit/
│   ├── __init__.py      # Public API
│   ├── checklist.py     # CheckResult, IntegrityContract, 10 check functions
│   ├── audit.py         # audit_experiment(), AuditResult, Verdict
│   ├── report.py        # generate_report(), generate_batch_report()
│   ├── cli.py           # argparse CLI (--experiment / --experiments-root)
│   └── mount.py         # Amplifier Tool protocol mount
├── tests/
│   ├── test_checklist.py  # 23 tests covering all 10 checks
│   ├── test_audit.py      # 10 tests including 8 spec-required
│   └── test_report.py     # 17 tests for Markdown report structure
├── pyproject.toml
└── README.md
```

---

## Running tests

```bash
cd modules/tool-experiment-audit
pip install -e .
python -m pytest tests/ -v
```

Expected: **50 tests, 0 failures**.

---

## Amplifier mount

The module registers an `experiment_audit` tool with the Amplifier coordinator:

```python
# In a session that loads this module:
result = experiment_audit(experiment_dir="experiments/production/a12a_v2")
# Returns: {"report": "# Experiment Audit Report...", "verdict": "FAIL"}
```

---

## Findings: first audit of amplifier-bundle-reflection

Running `--experiments-root experiments/` on the reflection bundle:

| Experiment | Records | Error Rate | Verdict |
|---|---|---|---|
| `a12a_v2_fixed` (validation) | 600 | **91.5%** | ❌ FAIL |
| `a4_n400` (validation) | 800 | **89.5%** | ❌ FAIL |
| `tier1_n300` (validation) | 1 200 | **49.8%** | ❌ FAIL |
| `handcrafted_a12a` (validation) | 600 | **46.3%** | ❌ FAIL |
| `sweep_n150` (exploratory) | 1 650 | **34.7%** | ❌ FAIL |
| `a12a_v2` (production) | 600 | **27.3%** | ❌ FAIL |
| `a12a_smoke1` (smoke) | 10 | 30.0% | ❌ FAIL |
| `a4_smoke2` (smoke) | 10 | 30.0% | ❌ FAIL |
| `sweep_20260419` (exploratory) | 4 | 0.0% | ❌ FAIL |
| `baseline_drift` (diagnostic) | 50 | 2.0% | ⚠️ SUSPICIOUS |

**No experiment passes outright.** Even the "production" `a12a_v2` run has 27.3% handler errors.
Do not trust downstream delta estimates until pipeline errors are resolved.
