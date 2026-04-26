# Experiment Block Hypothesis — Awareness Context

This document tells assistants when and how to use the
`amplifier-research-block-hypothesis` CLI tool (6th scientific-rigor capability
in the Research bundle).

---

## What This Tool Does

`tool-experiment-block-hypothesis` provides four subcommands for rigorously
evaluating whether a **persistent reflection block** (a JSON list of rules that
the model is instructed to follow) actually improves benchmark performance.

| Subcommand | One-line summary |
| ---------- | ---------------- |
| `analyze-rule-firing` | Heuristically estimate which rules in the block influenced critic outputs |
| `ablation-summary` | Paired Δ vs baseline for each experimental condition, with McNemar p |
| `domain-sensitivity` | Per-category help/hurt rates with BH-FDR correction across domains |
| `block-evaluation-verdict` | Apply pre-registered thresholds → WORKS / HETEROGENEOUS / DOES_NOT_WORK / UNDERPOWERED |

---

## When to Reach For This Tool

Suggest (or invoke) this tool when:

1. **After a block sweep** — you have `stage_traces.jsonl` from an experiment
   that used a reflection block and want to know which rules actually fired.

2. **Designing an ablation** — you want to compare (no-block / block-only /
   C3-only / C3+block) systematically.

3. **Pre-registered evaluation** — you have committed thresholds for "does the
   block work?" and want a reproducible verdict that can be referenced in a
   paper or report.

4. **Domain diagnosis** — accuracy improved overall but you suspect it's driven
   by specific subject domains (Math vs Biology etc.).

---

## Subcommand Reference

### `analyze-rule-firing`

```bash
amplifier-research-block-hypothesis analyze-rule-firing \
    --block /path/to/block.json \
    --traces /path/to/stage_traces.jsonl \
    --output rule_analysis.md
```

**Heuristics (all approximate):**
- Token-level overlap ≥ 25 % of rule tokens in critic output
- Any keyword (≥ 5 chars) from rule trigger/action in critic output
- Citation markers ("rule N", "[RN]", token literal)

**Caveats:** High fire rates (e.g., 80 %+ of all critic-producing traces) are
common because analytical critic language overlaps with rule vocabulary. A high
fire count does NOT prove the rule was explicitly invoked. Use citation markers
as the most reliable signal.

---

### `ablation-summary`

```bash
amplifier-research-block-hypothesis ablation-summary \
    --conditions C0,C3_alone,C3_block_only,C3_appendix_only,C3_both \
    --results-dir /path/to/experiment_results/ \
    --output ablation.md
```

The `--results-dir` must contain one `{condition}.jsonl` per condition.
Each file needs `item_id` and `correct_by_judge` per record.
Optionally `is_empty` for empty-rate computation.

**Outputs (per condition vs C0):**
- Paired Δ (pp), McNemar exact p, empty rate, help:hurt ratio
- Special `block_value_added` section when both `C3_alone` and `C3_block_only` present

---

### `domain-sensitivity`

```bash
amplifier-research-block-hypothesis domain-sensitivity \
    --results /path/to/results.jsonl \
    --items /path/to/items.jsonl \
    --baseline-approach A0 \
    --treatment-approach A12 \
    --output domain.md
```

`items.jsonl` must have `item_id` and `category` fields.
`results.jsonl` must have `item_id`, `approach_id`, `correct_by_judge`.

**Outputs:**
- Per-category help/hurt counts and rates
- McNemar exact p per category
- BH-FDR corrected q-values
- Significant categories highlighted (q < 0.05)

**Note:** Categories with n < 2 are flagged as dropped.

---

### `block-evaluation-verdict`

```bash
amplifier-research-block-hypothesis block-evaluation-verdict \
    --ablation-dir /path/to/splits/ \
    --baseline-condition C0 \
    --treatment-condition treatment \
    --threshold-paired-delta 5.0 \
    --threshold-substantive-delta 10.0 \
    --threshold-fdr 0.05 \
    --threshold-replication-splits 3 \
    --output verdict.json
```

`--ablation-dir` has one subdirectory per split, each containing
`{baseline}.jsonl` and `{treatment}.jsonl`.

**Verdict outcomes (in priority order):**

| Verdict | When |
| ------- | ---- |
| `UNDERPOWERED` | Delta ≥ threshold but McNemar power < 0.80 |
| `HETEROGENEOUS` | Split deltas vary ≥ 3pp AND combined p < fdr threshold |
| `WORKS` | Delta ≥ both thresholds AND p < fdr AND ≥ N positive splits AND range < 3pp |
| `DOES_NOT_WORK` | Default — delta too small, CI crosses zero, or not significant |

---

## Integration With Other Tools

- **tool-experiment-stage-analyzer** → runs first to understand empty-response origins;
  block-hypothesis runs second to understand *which rules* caused issues.
- **tool-experiment-power** → call before block-hypothesis to pre-register sample size;
  block-hypothesis references power when flagging UNDERPOWERED verdicts.
- **tool-experiment-audit** → run first to verify data integrity; block-hypothesis
  assumes clean, validated experiment directories.
- **tool-experiment-resume** → if a block sweep aborted mid-run, resume + merge first,
  then run block-hypothesis on the unified results.

---

## Honest Limitations

1. **Rule-firing is approximate.** Keyword heuristics have high false-positive rates
   on analytical text. Treat fire counts as indicative, not ground truth.

2. **"Helped" requires revert_decision.** If the experiment doesn't record
   `stages.revert_decision`, all non-empty fires will be classified as `neutral`.

3. **Small n warnings.** With < 30 discordant pairs, McNemar power < 0.80 for most
   realistic effect sizes. The tool will flag UNDERPOWERED rather than silently
   report an insignificant result.

4. **Domain sensitivity with many categories.** BH-FDR corrects for multiplicity,
   but with ≥ 20 categories the correction is conservative. Report raw p-values
   alongside q-values.
