# Experiment Integrity Awareness

Before trusting any experiment's accuracy numbers, run an integrity audit.
Pipeline failures can be disguised as results when `[HANDLER_ERROR]` or
`[ITEM_TIMEOUT]` placeholder records fill the JSONL — they have
`correct_by_judge: false` and look like genuine wrong answers, but are not.

---

## When to run an audit

Run `experiment_audit` (or the CLI) **before**:

- Reporting accuracy numbers from any experiment
- Computing deltas between approaches
- Citing help/hurt ratios in a write-up
- Comparing an experiment to a baseline

If the audit returns **FAIL** or **SUSPICIOUS**, do not trust downstream
statistics until the issue is understood.

---

## The integrity contract

Ten checks in five categories:

### 1. Completeness
| Check | What it catches |
|-------|----------------|
| `check_row_count` | Missing records — items that were never processed |
| `check_handler_error_rate` | `[HANDLER_ERROR]` / `[ITEM_TIMEOUT]` above 5% threshold |

### 2. Response sanity
| Check | What it catches |
|-------|----------------|
| `check_response_length_distribution` | Empty or truncated responses (broken generator) |
| `check_no_duplicate_responses` | Identical responses across items (stuck or cached) |

### 3. Judge integrity
| Check | What it catches |
|-------|----------------|
| `check_judge_coverage` | Records missing `correct_by_judge` (judge pipeline failed) |
| `check_judge_distribution` | Near-zero overall accuracy → judge or label bug |

### 4. Provenance
| Check | What it catches |
|-------|----------------|
| `check_manifest_present` | No manifest → cannot reproduce or verify lineage |
| `check_manifest_fields` | Manifest missing judge_model, split_sha256, or execution_seed |

### 5. Statistical sanity
| Check | What it catches |
|-------|----------------|
| `check_baseline_plausibility` | C0 accuracy < 1% or > 25% → wrong split or broken baseline |
| `check_help_hurt_ratio_reasonable` | Approach only helps or only hurts → suspicious |

---

## Verdict escalation

- Any ❌ **FAIL** → overall **FAIL** — do not trust results
- Any ⚠️ **WARN** (no FAIL) → overall **SUSPICIOUS** — investigate before citing
- All ✅ / ⏭️ → overall **PASS** — safe to proceed

---

## How to invoke

**Single experiment via CLI:**

```bash
python -m amplifier_research_audit \
    --experiment experiments/production/a12a_v2 \
    --expected-items 300 \
    --output audit_reports/a12a_v2_audit.md
```

**Batch — all experiments under a root:**

```bash
python -m amplifier_research_audit \
    --experiments-root experiments/ \
    --output audit_reports/full_audit.md
```

**Python API (inline, e.g., from a recipe step):**

```python
from pathlib import Path
from amplifier_research_audit import audit_experiment, generate_report

result = audit_experiment(Path("experiments/production/a12a_v2"))
if result.verdict.value != "PASS":
    print(generate_report(result))
    raise RuntimeError(f"Experiment failed audit: {result.verdict}")
```

**Amplifier tool (when this module is mounted):**

```
experiment_audit(experiment_dir="experiments/production/a12a_v2")
```

---

## Rationale for each check

| Check | Why it exists |
|-------|--------------|
| Handler error rate | Discovered in a12a_v2_fixed: 91.5% errors disguised as results |
| Response length | Empty responses score as wrong but are artifacts, not model failures |
| Duplicate responses | Stuck generator inflates item count without real diversity |
| Judge coverage | Missing labels bias accuracy estimates silently |
| Baseline plausibility | 0% baseline = judge or eval loop broken, not just hard items |
| Manifest presence | Without split_sha256 and execution_seed, runs cannot be reproduced |
| Help/hurt ratio | Extreme ratios (>5× or <0.2×) suggest data contamination or bug |

---

## Installing the tool

```bash
pip install -e modules/tool-experiment-audit/
```
