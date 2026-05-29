# Autonomous Experiment Loop Design

## Goal

Teach the `amplifier-bundle-research` bundle to reliably conduct the full empirical lifecycle — data collection → analysis → honest conclusion — for *any* scientific experiment, by gene-transferring the autonomous research loop from Andrej Karpathy's `autoresearch` repo as amplifier-native constructs only.

The output of the loop must be a defensible **finding**, not a hill-climb.

## Background

`autoresearch` is a GPU-bound PyTorch training harness. Its code is not reusable here — there is no GPU dependency, no CUDA, no training stack in this bundle. What *is* reusable is the **method**: its `program.md` protocol, which runs a tight autonomous loop:

```
propose → run → measure → keep/revert → log → repeat
```

…against a **frozen measurement apparatus** (the agent may edit `train.py`, but never `prepare.py` or the eval), using **git as the experiment ledger**.

That method is powerful but has known flaws that make its outputs hill-climbs rather than findings:

- **n=1 decisions** — keep/revert from a single run, no variance.
- **Greedy multiple-comparisons** — a long greedy search over one held-during-search metric is overfitting-prone and never corrected for.
- **No hypothesis** — changes are tweaks, not predictions.
- **Metric monoculture** — a single scalar with no guardrails invites silent regressions elsewhere.

This bundle (currently v0.8.5) already owns the *rigor organs* needed to discipline those flaws:

- pre-registration hash-lock (sha256) and `preregistration-reviewer`
- six `tool-experiment-*` Python modules (provenance, audit, power, resume, …)
- `statistician`, `honest-critic` agents
- `honest-pivot` and exploratory-labeling behaviors
- git (the keep/revert substrate)

What's missing is the **closed autonomous loop** that ties data → analysis → conclusion together. This design adds exactly that loop and wires autoresearch's discipline into the bundle's existing rigor organs.

## Approach

**Pattern transfer, not code merge.** We generalize autoresearch's loop to "any scientific experiment" and express it entirely in amplifier-native constructs: a skill (the method), a recipe (the engine), an agent (the scientist-in-the-loop), a template (the ledger), and a context file (when to use it). No new Python module, no new mode.

### Locked decisions (from brainstorm)

1. **Scope:** full closed system (not method-only, not method+recipe).
2. **Loop home:** fold into the existing `/execute` mode — no new mode. Plans without an `intervention_surface` never engage the loop and behave exactly as today; a plan that declares one engages the loop. `max_iterations: 1` is a degenerate single-iteration loop (not the legacy path — see the Dispatch contract and Edge cases).
3. **Proposer:** a NEW dedicated agent `experiment-runner` (not folded into `research-coordinator`).
4. **Ledger:** implemented as a TEMPLATE + recipe + git — NO new Python module.
5. **Experiment boundary:** an executable `run_command` emitting a primary scalar metric PLUS guardrail metrics (+ optional artifacts). Not single-metric (avoids monoculture); not a fully-open collect step (preserves comparability).
6. **Judge panel:** judgment-based metrics and the promotion-gate verdict use a cross-vendor multi-LLM judge panel (ensemble + meta-reviewer), pinned in the locked plan (see [Cross-vendor multi-LLM judge panel](#amendment--cross-vendor-multi-llm-judge-panel)).

## Architecture

Five NEW amplifier-native artifacts; no new Python module, no new mode.

| Artifact | Path | Role |
|----------|------|------|
| Skill | `skills/conducting-autonomous-experiments/SKILL.md` | The method itself — the real descendant of autoresearch's `program.md`: frozen-apparatus discipline, ledger rules, the promotion gate, the four anti-patterns. |
| Recipe | `recipes/autonomous-experiment-loop.yaml` | The engine — a `while`/`break_when` loop (propose → collect → analyze → decide → log); invoked by `/execute` when a locked plan defines an intervention surface + metric. |
| Agent | `agents/experiment-runner.md` | The scientist-in-the-loop — given the locked plan + ledger, proposes the next intervention with rationale, applies keep/revert after analysis. `model_role: reasoning`. |
| Template | `templates/experiment-ledger.yaml` | The disciplined descendant of autoresearch's `results.tsv` — the schema for each iteration row. |
| Context | `context/autonomous-loop-awareness.md` | When to use the loop, and its honest limits. |

### Dispatch contract

`modes/execute.md` is **EDITED** (it is a modified file, not unchanged) to detect when the locked pre-registration declares an `intervention_surface`:

- **Present** → `execute.md` invokes `recipes/autonomous-experiment-loop.yaml`.
- **Absent** → `execute.md` behaves exactly as today (single-pass), unchanged in observable output.

No NEW mode is added; the loop is reached purely through this dispatch.

### Reused unchanged

- All six `tool-experiment-*` modules.
- `preregistration-reviewer`.
- `statistician` + `tool-experiment-power`.
- `honest-critic` / `honest-pivot` / exploratory-labeling.
- git — the keep/revert substrate.

### Skills source

`skills/` does not yet exist in this bundle — `conducting-autonomous-experiments` is its first owned skill. Implementation note: `bundle.md` must declare/confirm the skills source so `skills/conducting-autonomous-experiments/SKILL.md` is discoverable (per the tool-skills config pattern).

### Boundary discipline

> **Recipe orchestrates. Agent decides. Tools compute. Skill teaches.**

Only `bash` (the `run_command`) and `git` touch the filesystem at runtime; both are already safe within `/execute`.

## Components

### Section 1 — The frozen apparatus (scientific core)

We reproduce autoresearch's "agent may edit `train.py`, never `prepare.py`/eval" discipline. The frozen declarations live inside the bundle's **existing** sha256 pre-registration hash-locked plan — no new lock mechanism. Their *enforcement* (intervention-surface/measurement-protocol disjointness, and rejecting out-of-surface commits) is NEW recipe logic: a `bash` gate that checks changed files (`git diff --name-only`) against the frozen `intervention_surface` allowlist.

During `/study-plan`, the locked pre-registration is extended to declare four **frozen** things:

1. **`intervention_surface`** — the file(s)/parameters the loop may mutate (≈ `train.py`).
2. **`measurement_protocol`** — the `run_command` + how the primary metric is parsed (≈ the frozen eval). Includes the judge panel when the metric is LLM-judged (see Amendment).
3. **`primary_metric` + direction + keep/revert decision rule** — e.g., keep iff the primary improves beyond noise AND no guardrail regresses past tolerance.
4. **`guardrail_metrics` + tolerances, stopping rule** (`max_iterations`, `patience`, `budget`), **seeds**, AND the **held-out confirmation set/seeds** reserved for the promotion gate.

All four live inside the hash-locked plan. `preregistration-reviewer` gains a checklist item:

> "intervention surface and measurement protocol are disjoint and frozen."

Changing the apparatus requires a NEW pre-registration (new hash) — never an in-loop edit. This procedurally prevents goalpost-moving (silently tuning the metric until results look good); the apparatus is sealed before any data is seen.

### Section 2 — Loop mechanics & the `experiment-runner` agent

The engine is `recipes/autonomous-experiment-loop.yaml` (a `while`/`break_when` loop). One iteration:

1. **PROPOSE** — `experiment-runner` reads the locked plan + ledger-so-far and proposes the next intervention WITH a written rationale and a directional prediction. Every change is a mini-hypothesis, not a random tweak — the discipline autoresearch lacks. It edits only files inside the frozen `intervention_surface` and commits (git = keep/revert substrate).
2. **COLLECT** — the recipe runs the frozen `run_command` via `bash` under the pre-registered budget, repeated across the declared seeds; stdout/artifacts captured. Before the FIRST run, `tool-experiment-provenance-check`'s pre-experiment gate confirms all input data files are git-tracked (hard stop if not).
3. **ANALYZE** — primary + guardrail metrics are parsed per seed; `statistician` / `tool-experiment-power` compute mean + variance across seeds (n>1, fixing autoresearch's n=1 flaw); `tool-experiment-audit` checks run integrity (handler errors, empty/duplicate outputs).
4. **DECIDE** — `experiment-runner` applies the pre-registered keep/revert rule (keep iff the primary improves beyond noise AND no guardrail regresses past tolerance). Keep → advance branch; reject → `git reset --hard HEAD~1` on the intervention commit only. Every outcome is stamped **exploratory** by default.
5. **LOG** — append a ledger row and commit the ledger *separately, after* the keep/revert decision (never in the same commit as the intervention), so a reverted intervention never deletes ledger rows.

**Stop conditions** (from the locked plan): `max_iterations` reached, `patience` exhausted (N iterations with no kept improvement → plateau), or `budget` consumed. `max_iterations: 1` is a degenerate single-iteration loop; plans without an `intervention_surface` never engage the loop at all and behave exactly as today.

**Boundaries:** recipe = control flow; agent = scientific judgment; tools = compute; git = record. The agent never touches the measurement protocol or stopping rule (frozen).

### Section 3 — The promotion gate (the rigor differentiator)

Inside the loop, everything is **exploratory** — greedy search over a metric is overfitting-prone and multiple-comparisons-laden. No loop result is ever stated as a conclusion; it is a *candidate*. The gate is an explicit recipe stage that runs AFTER the loop terminates:

1. **Select candidate(s)** — the kept interventions on the final branch (the running optima the loop discovered).
2. **Confirmatory re-run** — re-execute each candidate's frozen `run_command` on a **held-out confirmation set/seeds the loop never touched** (declared in the locked plan). This breaks the search/validation entanglement.
3. **Statistical adjudication** — `statistician` + `tool-experiment-power` evaluate against the pre-registered alpha and apply **Benjamini–Hochberg** correction across the number of candidates promoted (the bundle default). `tool-experiment-audit` confirms the confirmation run's integrity.
4. **Verdict** — only candidates clearing corrected significance AND respecting guardrails get their ledger label flipped **exploratory → confirmatory**. Everything else stays exploratory, honestly.
5. **Honest pivot** — `honest-critic` + `honest-pivot` review the gate output; if nothing confirms, the recipe says so plainly and the downstream `/draft` reports a null/exploratory result rather than dressing up noise.

**Held-out set is non-negotiable:** reusing the loop's own measurement to "confirm" is the canonical p-hacking trap. The gate is the firewall. This stage is pure orchestration over existing tools — no new code.

## Data Flow

### The ledger template

New file `templates/experiment-ledger.yaml` — structured YAML (not TSV), one row per iteration, appended by the recipe. It is the disciplined descendant of autoresearch's `results.tsv`: structured so it carries the rigor metadata autoresearch omits.

Example row structure:

```yaml
- iteration: 7
  prereg_hash: "sha256:abc123…"        # binds row to the frozen apparatus
  commit: "a1b2c3d"                     # the kept/reverted intervention
  intervention: "increase MLP width 512→768"
  rationale: "capacity-bound; predict primary improves"
  prediction: "primary ↓ ≥ 0.5%"
  seeds: [0, 1, 2]
  primary_metric: {name: val_bpb, values: [0.812, 0.809, 0.814], mean: 0.8117, sd: 0.0025}
  guardrail_metrics:
    - {name: peak_vram_mb, mean: 38120, tolerance: "≤ 40000", regressed: false}
  decision: keep                        # keep | revert
  decision_reason: "primary improved beyond 2×sd; no guardrail regression"
  label: exploratory                    # exploratory by default; promotion gate appends a confirmation: block (not in-place edit)
  audit_verdict: PASS                   # from tool-experiment-audit
  artifacts: ["run.log", "loss_curve.png"]
  timestamp: "2026-05-29T07:30:00Z"
```

### Data flow per iteration

```
experiment-runner proposes + commits the intervention (intervention commit)
  → recipe runs `bash` collect across seeds
  → tools populate metrics / audit
  → experiment-runner decides keep/revert
  → if revert: `git reset --hard HEAD~1` on the intervention commit only
  → append the ledger row (intervention / rationale / prediction / decision / decision_reason)
  → commit the ledger SEPARATELY (its own commit, after the decision)
  → row finalized
```

The ledger file is **committed separately and after** the keep/revert decision — never in the same commit as the intervention — and it is **tracked but lives outside the `intervention_surface`**, so it is never part of a reverted commit. This is why "a broken intervention is data": reverting the intervention with `git reset --hard HEAD~1` removes only the intervention's code change, while the ledger row recording that failure is committed afterward and survives.

The git SHA in `commit` links each row to its diff, so the ledger + git history together reconstruct the entire search. The promotion gate later **appends a `confirmation:` block (carrying the new label)** to a confirmed candidate's row rather than mutating the existing row in place, preserving the ledger's append-only audit property.

The ledger lives at the study's working dir (e.g. `experiments/<study>/ledger.yaml`); the template ships the schema + a header comment, not a location mandate.

## Error Handling

### Failure handling within the loop (descended from autoresearch's crash/timeout policy)

- **Run crash / non-zero exit** → `git reset --hard HEAD~1` on the intervention commit, *then* append the ledger row (`decision: revert`, `audit_verdict: ERROR`) and commit the ledger separately; the loop continues (a broken intervention is data, not a stop — the ledger row survives the revert because it lives outside `intervention_surface` and is committed after the reset).
- **Budget timeout** → that seed is recorded as incomplete; if a quorum of seeds fail, the iteration is reverted.
- **Integrity failure** (`tool-experiment-audit` returns FAIL/SUSPICIOUS — handler-error cascade, empty/duplicate outputs) → the iteration's metrics are NOT trusted; auto-revert and flag the row.
- **Provenance gate fails** (untracked input data) → hard stop *before* iteration 1; the loop refuses to start.
- **Intervention escapes the frozen surface** (the runner edits a file outside `intervention_surface`) → the recipe rejects the commit and re-prompts the runner; never silently allowed.

### Edge cases

- **`max_iterations: 1`** → a degenerate single-iteration loop (it still runs the loop code path and emits `ledger.yaml`; it is NOT byte-identical to today's `/execute`, which emits `execution-log.yaml`/`evidence-log.yaml`). Backward compatibility comes from the Dispatch contract: plans *without* an `intervention_surface` never engage the loop and behave exactly as today.
- **Plateau** (`patience` exhausted, no kept improvement) → terminate honestly, carry best-so-far into the promotion gate.
- **Promotion gate confirms nothing** → the recipe returns a null result; `/draft` reports it as such (honest-pivot).
- **Loop interrupted/resumed** → `tool-experiment-resume` (plan/subset/merge) reconciles partial ledgers; the ledger + git history are the resumable state.

## Testing Strategy

No new Python, so testing is at the config/integration layer:

- **Recipe validation** via `recipes validate` (schema correctness) + `recipes:result-validator` against intent.
- **Smoke test:** a trivial frozen experiment (≈5-line script emitting a metric) drives 3 iterations end-to-end, asserting keep/revert, ledger rows, and promotion-gate behavior — modeled on the existing `_smoke-*.yaml` recipes.
- **`experiment-runner` exercised in the smoke loop:** proposes within the surface, respects the frozen protocol, applies the decision rule.
- **The six `tool-experiment-*` modules keep their existing pytest suites unchanged.**

## Amendment — Cross-vendor multi-LLM judge panel

Wherever the loop relies on **judgment** rather than a deterministic number, the design uses a **cross-vendor multi-LLM judge panel** (e.g., Claude Opus 4.8 + GPT-5.5) — never a single model — directly reusing the bundle's existing cross-vendor-judge assets (`behaviors/cross-vendor-judge.md`, `context/orchestrated-loop-judge-rubric.md`) and the `agents/ml-paper-reviewer.md` ensemble + meta-reviewer pattern. It applies at three points:

1. **LLM-judged metrics in the loop (Section 2, COLLECT/ANALYZE).** autoresearch's `val_bpb` is deterministic, but "anything scientific" includes LLM-judged outcomes (correctness, quality). When the pre-registered `primary_metric` or a guardrail requires a judge, **each item is scored by the panel**; the metric is the agreed score, and **inter-judge agreement (Cohen's κ)** is recorded per iteration. The judge panel + their models are part of the **frozen** measurement protocol (Section 1) — judges cannot be swapped mid-loop to manufacture a win.

2. **Promotion gate adjudication (Section 3).** The confirmatory verdict runs as an **ensemble + meta-reviewer**: each vendor model judges the held-out confirmation run independently, then a meta-reviewer reconciles. A candidate is promoted to **confirmatory** only on panel agreement AND corrected statistical significance. Per-judge verdicts + the meta verdict are stored in the ledger's `confirmation:` block.

3. **Judge integrity (Error Handling).** `tool-experiment-audit` already checks judge coverage/distribution; with a panel we additionally **flag low inter-judge agreement** (κ below a pre-registered threshold) as a SUSPICIOUS verdict — because judges disagreeing means the metric isn't trustworthy, regardless of the score.

Panel composition (models, count, meta-reviewer) is configurable via the routing matrix / provider preferences, defaulting to a 2–3 model cross-vendor set with a meta-reviewer, pinned in the locked plan for reproducibility.

## Open Questions / Non-Goals

### Non-goals

- Porting autoresearch's PyTorch/CUDA training code or any GPU dependency. **Pattern transfer only.**
- (This cut) Vendoring a Mac-runnable autoresearch fork as an example target (was "Option B"; deferred).

### Open questions

- Exact default κ threshold for the judge-disagreement SUSPICIOUS flag (pin during implementation). It should be pinned in the pre-registration template **schema** (not left implicit), so it is hash-locked per study.
- Whether the loop recipe extends the existing `orchestrated-loop.yaml` or stands alone. **Lean:** stand-alone sibling — `orchestrated-loop` adjudicates residuals, whereas this optimizes a scalar metric over interventions — but confirm in `/write-plan`. Note this choice also affects whether `tool-experiment-resume` can reconcile partial ledgers (a stand-alone recipe owns its own resumable ledger state; extending `orchestrated-loop` would need the resume contract threaded through that recipe's state).

### Attribution

- Credit Karpathy / `autoresearch` (MIT) in the new files' provenance and the eventual bundle README.
- Version bump target: 0.8.5 → 0.9.0.
