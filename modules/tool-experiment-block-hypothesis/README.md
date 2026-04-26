# tool-experiment-block-hypothesis

**Scientific evaluation toolkit for persistent reflection blocks.**

Determines whether a block of reflection rules (e.g., `hle_handcrafted.json`) actually
improves agent performance on a benchmark, and which individual rules are responsible.

## Subcommands

| Subcommand | What it does |
| ---------- | ------------ |
| `analyze-rule-firing` | Heuristic detection of per-rule influence in stage-trace critic outputs |
| `ablation-summary` | Multi-condition paired comparison table (Δ vs baseline, McNemar p, empty rate) |
| `domain-sensitivity` | Per-category help/hurt rates with stratified McNemar + BH-FDR correction |
| `block-evaluation-verdict` | Pre-registered threshold evaluation → WORKS / HETEROGENEOUS / DOES_NOT_WORK / UNDERPOWERED |

## Quick Start

```bash
# 1. Per-rule firing analysis
amplifier-research-block-hypothesis analyze-rule-firing \
    --block data/blocks/hle_handcrafted.json \
    --traces experiments/production/q1_phase2/stage_traces.jsonl \
    --output rule_analysis.md

# 2. Ablation comparison
amplifier-research-block-hypothesis ablation-summary \
    --conditions C0,C3_alone,C3_block_only,C3_both \
    --results-dir experiments/ablation/ \
    --output ablation.md

# 3. Domain sensitivity
amplifier-research-block-hypothesis domain-sensitivity \
    --results experiments/production/results.jsonl \
    --items data/items.jsonl \
    --baseline-approach A0 --treatment-approach A12 \
    --output domain.md

# 4. Pre-registered verdict
amplifier-research-block-hypothesis block-evaluation-verdict \
    --ablation-dir experiments/splits/ \
    --threshold-paired-delta 5.0 \
    --threshold-substantive-delta 10.0 \
    --threshold-fdr 0.05 \
    --threshold-replication-splits 3 \
    --output verdict.json
```

## Data Formats

### Block JSON (`block.json`)
```json
{
  "name": "my_block",
  "rules": [
    {
      "mechanism": "ARITHMETIC_ERROR",
      "trigger": "...",
      "action": "...",
      "token": "RT_CHECK_ARITHMETIC",
      "validated": true
    }
  ]
}
```

### Results JSONL (`results.jsonl`) — one record per (item_id × approach_id)
```json
{"item_id": "abc123", "approach_id": "A0", "correct_by_judge": false, "is_empty": false}
{"item_id": "abc123", "approach_id": "A12", "correct_by_judge": true, "is_empty": false}
```

### Items JSONL (`items.jsonl`) — one record per item
```json
{"item_id": "abc123", "category": "Math"}
```

### Ablation directory structure (for `block-evaluation-verdict`)
```
ablation_dir/
  split_0/
    C0.jsonl
    treatment.jsonl
  split_1/
    C0.jsonl
    treatment.jsonl
  split_2/
    C0.jsonl
    treatment.jsonl
```

## Verdict Rules (in order)

1. **UNDERPOWERED** — combined delta ≥ threshold but McNemar power < 0.80
2. **HETEROGENEOUS** — split deltas vary ≥ 3pp AND combined McNemar p < α
3. **WORKS** — delta ≥ both thresholds AND p < α AND ≥ N positive splits AND range < 3pp
4. **DOES_NOT_WORK** — default (delta too small or CI crosses zero)

## Rule-Firing Heuristics

`analyze-rule-firing` uses three heuristics (approximations only):

1. **Token-level overlap** — fraction of rule tokens (≥5 chars) appearing in critic output ≥ 25%
2. **Keyword substring** — any distinctive keyword from trigger/action appears in critic output
3. **Citation markers** — explicit "Rule N", "[RN]", or token literal in critic output

**Important:** These heuristics produce false positives because analytical critic outputs
often contain vocabulary matching rule keywords even when the rule didn't specifically fire.
High fire rates across all rules should be interpreted as "rule vocabulary is topically
relevant" rather than "rule was explicitly invoked." Use citation markers (Heuristic 3) as
the most reliable signal.

## Smoke Test Results — Phase 2 Production Data

Running `analyze-rule-firing` on `hle_handcrafted.json` against
`experiments/production/q1_phase2_n200/stage_traces.jsonl` (400 traces, 200 items × A0/A12a):

| Rule | Fires | Hurt (empty) | Neutral |
|------|------:|-------------:|--------:|
| RT_CHECK_ABSTRACTION_LEVEL | 168 | 69 | 99 |
| RT_CONSIDER_UNUSUAL_ANSWER | 166 | 70 | 96 |
| RT_CHECK_ALL_OPTIONS | 164 | 70 | 94 |
| RT_REREAD_STEM_CONSTRAINTS | 163 | 68 | 95 |
| RT_VERIFY_FACTUAL_CLAIM | 163 | 70 | 93 |
| RT_VERIFY_SPATIAL_STATE | 160 | 70 | 90 |
| RT_RECHECK_DERIVATION | 155 | 69 | 86 |

**Interpretation:**
- All 7 rules fire on 155–168 of 199 critic-producing traces — fire rates ≥ 78%.
  This is expected: HLE critic outputs are analytical paragraphs whose vocabulary
  overlaps with rule keywords at high rates (Heuristic 2).
- `RT_RECHECK_DERIVATION` fires least (155) — consistent with math/derivation keywords
  being more specific than general analytical vocabulary.
- `RT_CHECK_ABSTRACTION_LEVEL` fires most (168) — "cause", "level", "root", "dominant"
  appear in many HLE critiques.
- **No "dead weight" rule by fire count alone.** The ~13 pp spread (155 vs 168) is
  marginal noise, not a meaningful signal. Ground-truth per-item tagging would be needed
  to identify truly unused rules.
- Hurt counts (~68–70) match the known ~70 empty responses in the A12a condition.
  Helped = 0 because this dataset records no `revert_decision` fields.
