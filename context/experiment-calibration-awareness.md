# Experiment Calibration Awareness

The research bundle includes ECE/Brier-score calibration analysis as a first-class metric for any experiment that elicits per-item confidence from an agent.

## Why calibration matters

Accuracy alone does not determine deployment-readiness. An 80%-accurate agent that is confidently wrong on its 20% misses is harder to deploy safely than a 70%-accurate agent that knows when it's unsure. **Calibration measures the gap between an agent's stated confidence and its actual accuracy at that confidence**, and is the single most important metric for downstream escalation logic.

The PSE-PG14 v4d paper elevated calibration alongside accuracy in §"Calibration" because deployment teams cannot build escalation rules around accuracy without calibration.

## When to use it

Calibration analysis applies whenever:

- The agent is asked to provide a confidence score on each answer
- Deployment will use the confidence to decide whether to act, escalate, or ask for human input
- The benchmark includes any items where the agent CAN admit uncertainty (refuse, say "not sure", give a low-confidence answer)

It does NOT apply to benchmarks where the agent always commits to a single answer with no confidence signal — for those, accuracy + Wilson CI is sufficient.

## Three first-class metrics

| Metric | Definition | When to report |
|---|---|---|
| **ECE** (Expected Calibration Error) | Average gap between confidence and accuracy, weighted by bin size | Always when calibration is requested |
| **Brier score** | Mean squared error between confidence and outcome | Use when comparing to other ML literature |
| **Reliability diagram** | Per-bin scatter of `(stated_confidence, actual_accuracy)` with diagonal | Always for figures/visualization |

ECE is the headline number. Brier provides cross-paper comparability. The reliability diagram is the visual gut-check.

## How to elicit confidence (the elicitation prompt matters)

Ill-posed: "Are you sure?" → produces over-confident answers.
Well-posed: "On a 0–100 scale, how confident are you that your answer is correct? Consider your confidence as the probability that, if I checked your answer against an authoritative source, it would be correct."

PSE-PG14 v4d publishes its exact elicitation prompt in the paper appendix. Any new benchmark in this bundle should publish its elicitation prompt explicitly in the rubric document.

## Reliability binning

Default: 10 bins of width 0.10. Each bin holds the items whose confidence falls in that range. ECE is the size-weighted average vertical distance from the diagonal.

```
ECE = sum_b (n_b / N) * |conf_b - acc_b|
```

where `n_b` is items in bin `b`, `conf_b` is the mean confidence in bin `b`, `acc_b` is the actual accuracy in bin `b`.

## Worked example (PSE-PG14 v4d)

Stated confidence on the F4–F6 rubric subsample, n=42, bins of width 0.10:

| Bin | n | mean confidence | actual accuracy | gap |
|-----|---|------------------|------------------|-----|
| 0.50–0.60 | 0 | — | — | — |
| 0.60–0.70 | 2 | 0.66 | 0.50 | 0.16 |
| 0.70–0.80 | 8 | 0.74 | 0.62 | 0.12 |
| 0.80–0.90 | 17 | 0.84 | 0.76 | 0.08 |
| 0.90–1.00 | 15 | 0.94 | 0.93 | 0.01 |

ECE = (2/42)(0.16) + (8/42)(0.12) + (17/42)(0.08) + (15/42)(0.01) = 0.069

The agent is over-confident at the low end (says 66% when right 50%) and well-calibrated at the high end. A deployment decision that requires confidence ≥ 0.90 to skip human review is well-served by this agent's calibration in that band; a decision that uses 0.70 as the threshold should expect substantial errors.

## Tool integration

`tool-experiment-power` is being extended to compute ECE and Brier given a JSONL file of `{item_id, confidence, correct}` records. The CLI:

```bash
python -m tool_experiment_power calibration \
    --records data/v3_run_with_confidence.jsonl \
    --bins 10 \
    --output validation/calibration_report.json
```

Output JSON:
```yaml
calibration_report:
  n: 130
  bins: 10
  ece: 0.069
  brier: 0.082
  reliability_diagram_data:
    - {bin: 0, lo: 0.0, hi: 0.1, n: 0}
    - {bin: 6, lo: 0.6, hi: 0.7, n: 2,  mean_conf: 0.66, mean_acc: 0.50, gap: 0.16}
    # ...
```

## Honest residuals (PSE-PG14 v4d's calibration limitations)

- Confidence is elicited only for rubric-graded items (F4–F6); fact-retrieval items in F1–F4 are deterministic and do not produce a confidence signal.
- The bin sizes are small at the low end (n=2 in the 0.60–0.70 bin), so the per-bin estimates are noisy. Consider variable-width bins or report Wilson CIs per bin for n < 20.
- Calibration is conditional on the elicitation prompt; a different prompt produces a different ECE. The prompt is published; the result is not the only reasonable one.

## Integration with the orchestrated loop

A round of the orchestrated-loop recipe that targets calibration improvement should:
1. Measure baseline ECE
2. Propose a bundle overlay that changes the elicitation prompt or adds a confidence-calibration training signal
3. Re-measure ECE
4. Adjudicate "calibration-improved" iff ECE_after < ECE_before with bootstrap CI excluding 0
