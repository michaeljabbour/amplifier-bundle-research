# tool-experiment-stage-analyzer

Reusable **empty-response root-cause analyzer** for staged reflection experiments.
Fourth scientific-rigor tool in the Amplifier research bundle — sibling to
`tool-experiment-audit`, `tool-experiment-resume`, and `tool-experiment-power`.

## Purpose

When a reflection pipeline produces empty final responses, the failure can originate
at three different stages: the **generator** (didn't produce content), the **critic**
(produced empty output that the revert logic propagated), or the **revert decision**
(chose an empty response despite both stages having content).

This tool ingests `stage_traces.jsonl`, classifies each empty-final record into one
of six failure-mode categories, and applies the pre-registered H1a/H1b confirmation
criteria from the reflection-tokens pre-registration §2.3.

## Installation

```bash
pip install -e modules/tool-experiment-stage-analyzer/
```

## CLI

### `analyze` — full pipeline → Markdown report

```bash
amplifier-research-stage-analyzer analyze \
    --traces experiments/foo/stage_traces.jsonl \
    --output reports/stage_analysis.md
```

Ingests traces → categorizes by failure mode → applies H1 criteria → writes Markdown.

### `hypothesis-test` — H1a/H1b verdicts → JSON

```bash
amplifier-research-stage-analyzer hypothesis-test \
    --traces experiments/foo/stage_traces.jsonl \
    --output verdicts.json
```

Emits `{"h1a_confirmed": bool, "h1a_fraction": float, "h1b_confirmed": bool, "h1b_fraction": float, "evidence": [...]}`.

## Python API

```python
from amplifier_research_stage_analyzer.ingest import ingest_stage_traces
from amplifier_research_stage_analyzer.categorize import categorize_empty
from amplifier_research_stage_analyzer.analyze import test_h1_hypotheses
from amplifier_research_stage_analyzer.report import generate_report

records = ingest_stage_traces("experiments/foo/stage_traces.jsonl")
cat = categorize_empty(records)
hyp = test_h1_hypotheses(cat)
md = generate_report({
    "categorize": cat,
    "hypothesis": hyp,
    "total_records": len(records),
    "total_empty": sum(cat["counts"].values()),
})
```

## Input schema — `stage_traces.jsonl`

Each line is a JSON object:

```json
{
  "item_id": "string",
  "approach_id": "string",
  "approach_name": "string",
  "stages": {
    "generator": {
      "output": "string",
      "output_length": 200,
      "latency_ms": 1500.0,
      "cost_usd": 0.001,
      "is_empty": false,
      "is_truncated": false
    },
    "critic": null,
    "revert_decision": null
  },
  "final_response_length": 200,
  "final_is_empty": false,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

`critic` and `revert_decision` may be `null` for A0-style (no-reflection) records.

## Failure-mode categories

| Category | Meaning | Hypothesis |
|---|---|---|
| `gen_substantive_critic_empty` | Generator ≥100 chars, critic empty | H1b evidence |
| `gen_substantive_critic_substantive` | Both ≥100 chars, final still empty | H1a evidence |
| `gen_empty_critic_substantive` | Generator empty, critic substantive | Revert preserved empty |
| `gen_empty_critic_empty` | Both empty | Both stages failed |
| `gen_substantive_no_critic` | A0 record, generator non-empty, final empty | Anomaly |
| `unknown` | Schema gaps | — |

## Hypothesis tests (pre-registered §2.3)

| Hypothesis | Criterion | Confirmed if |
|---|---|---|
| **H1a** | Reflection stage is the failure source | `(gen_sub_crit_sub + gen_sub_crit_empty) / total ≥ 0.40` |
| **H1b** | Critic empty output is the proximate cause | `gen_sub_crit_empty / total ≥ 0.40` |

## Tests

```bash
pytest modules/tool-experiment-stage-analyzer/tests/ -v
# 25 tests, all passing
```

## Relationship to sibling tools

| Tool | Purpose |
|---|---|
| `experiment_audit` | Integrity audit before trusting experiment results |
| `experiment_resume` | Repair aborted runs — plan / subset / merge |
| `experiment_power` | Pre-register sample sizes; compute MDE and post-hoc power |
| `experiment_stage_analyzer` | Root-cause analysis of empty-response failures by stage |
