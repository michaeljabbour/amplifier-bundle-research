# Experiment Stage Analyzer Awareness

The research bundle includes `tool-experiment-stage-analyzer` — a first-class capability
for empty-response root-cause analysis of staged reflection experiments.

## When to use it

Use `experiment_stage_analyzer` / `amplifier-research-stage-analyzer` whenever you need to:

- **Diagnose empty responses** from a generator → critic → revert pipeline.
- Determine whether failures originate in the generator, critic, or revert-decision stage.
- **Apply pre-registered H1a/H1b criteria** (reflection-tokens pre-registration §2.3)
  to categorize and confirm hypotheses about the failure mode.
- Produce a **structured Markdown report** for inclusion in a research write-up.

## The two subcommands

| Subcommand | Question answered | Inputs → Output |
|---|---|---|
| `analyze` | Where do empty responses come from? | stage_traces.jsonl → **Markdown report** |
| `hypothesis-test` | Do the H1 hypotheses confirm? | stage_traces.jsonl → **JSON verdicts** |

---

## Failure-mode categories

| Category | Meaning | Hypothesis signal |
|---|---|---|
| `gen_substantive_critic_empty` | Generator ≥100 chars; critic empty | H1b evidence |
| `gen_substantive_critic_substantive` | Both ≥100 chars; final still empty | H1a evidence |
| `gen_empty_critic_substantive` | Generator empty; critic non-empty | Revert preserved empty |
| `gen_empty_critic_empty` | Both stages empty | Both stages failed |
| `gen_substantive_no_critic` | A0-style record, non-empty gen, empty final | Anomaly |
| `unknown` | Schema gaps | — |

---

## Pre-registered confirmation criteria (§2.3)

| Hypothesis | Criterion | Threshold |
|---|---|---|
| **H1a** | Reflection is the root cause | `(gen_sub_crit_sub + gen_sub_crit_empty) / total_empties ≥ 0.40` |
| **H1b** | Critic empty output is the proximate cause | `gen_sub_crit_empty / total_empties ≥ 0.40` |

---

## How to invoke

### CLI

```bash
# Full analysis → Markdown report
amplifier-research-stage-analyzer analyze \
    --traces experiments/foo/stage_traces.jsonl \
    --output reports/stage_analysis.md

# Hypothesis verdicts only → JSON
amplifier-research-stage-analyzer hypothesis-test \
    --traces experiments/foo/stage_traces.jsonl \
    --output verdicts.json
```

### Python API

```python
from amplifier_research_stage_analyzer.ingest import ingest_stage_traces
from amplifier_research_stage_analyzer.categorize import categorize_empty
from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
from amplifier_research_stage_analyzer.report import generate_report

records = ingest_stage_traces("experiments/foo/stage_traces.jsonl")
cat = categorize_empty(records)
hyp = test_h1_hypotheses(cat)
md = generate_report({
    "categorize": cat, "hypothesis": hyp,
    "total_records": len(records),
    "total_empty": sum(cat["counts"].values()),
})
```

### Amplifier tool protocol

```
experiment_stage_analyzer(operation="analyze",
                           traces_path="experiments/foo/stage_traces.jsonl",
                           output_path="reports/stage_analysis.md")
```

---

## Relationship to sibling tools

| Tool | Purpose |
|---|---|
| `experiment_audit` | Verify experiment data integrity before trusting results |
| `experiment_resume` | Repair aborted runs — plan / subset / merge |
| `experiment_power` | Pre-register sample sizes; compute MDE and post-hoc power |
| `experiment_stage_analyzer` | Root-cause analysis of empty-response failures by stage |

**Typical staged-experiment workflow**:
1. Run `experiment_audit` on the sweep output to verify data integrity.
2. Run `experiment_stage_analyzer analyze` to categorize empty-response failures.
3. Run `experiment_stage_analyzer hypothesis-test` to apply pre-registered criteria.
4. Include verdicts in your write-up alongside the power analysis from `experiment_power`.

## Installing the tool

```bash
pip install -e modules/tool-experiment-stage-analyzer/
```
