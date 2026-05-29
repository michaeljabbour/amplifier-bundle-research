# Autonomous Experiment Loop — Awareness

When a locked pre-registration declares an `experiment_loop` block, `/execute`
runs the autonomous experiment loop instead of a single pass. The method lives
in `skills/conducting-autonomous-experiments/SKILL.md`.

---

## When to reach for the loop

Use the autonomous loop **only when ALL of the following hold:**

1. **Executable measurement** — a `run_command` that emits a primary scalar
   metric, repeatable across seeds.
2. **Mutable intervention surface** — an `intervention_surface` that is
   disjoint from the frozen measurement protocol; you can vary interventions
   without touching the eval apparatus.
3. **Causal question** — the question is "which intervention moves the metric?"
   not "what does the metric say about the world?"
4. **Reserved confirmation set** — a held-out set (or seeds) that has not been
   touched by the search loop.

If any of these is missing, **do NOT declare an `experiment_loop` block.**
Plans without one run `/execute` single-pass, unchanged.

---

## Honest limits

- **Loop result is a candidate, not a conclusion.** Everything the loop finds
  is exploratory until the held-out promotion gate runs.
- **Greedy search ≠ confirmatory result.** The loop performs greedy search
  over the intervention surface; that search is inherently exploratory and
  subject to selection effects.
- **Only the held-out promotion gate flips the finding to confirmatory.** A
  finding that does not survive the held-out set is still honest and publishable
  — as a null result.
- **If nothing confirms, that is the finding.** An honest null is a valid
  outcome. Do not re-run the loop on the held-out set to recover a positive.
- **The apparatus is frozen.** Changing the primary metric, measurement
  protocol, stopping rule, seeds, or held-out set after the loop starts
  requires a **new pre-registration**. Retroactive changes invalidate the
  confirmatory status of any result.

---

## Related

| Resource | Location |
|---|---|
| Method (SKILL.md) | `skills/conducting-autonomous-experiments/SKILL.md` |
| Engine recipe | `recipes/autonomous-experiment-loop.yaml` |
| Frozen apparatus fields | `templates/preregistration.yaml` |
| Ledger schema | `templates/experiment-ledger.yaml` |
| Judge panel (3 files) | `behaviors/cross-vendor-judge.md`, `context/orchestrated-loop-judge-rubric.md`, `agents/ml-paper-reviewer.md` |
