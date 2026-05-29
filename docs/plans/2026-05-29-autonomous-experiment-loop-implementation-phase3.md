# Autonomous Experiment Loop — Implementation Plan, Phase 3 (Promotion Gate + Judge Panel + Skill/Context + End-to-End Smoke + Attribution)

> **Execution:** Use the subagent-driven-development workflow to implement this plan.
> **For execution:** use `/execute-plan`.

**Goal:** Close the loop into a defensible FINDING: the held-out promotion-gate sub-recipe (confirmatory re-run + Benjamini–Hochberg correction + cross-vendor multi-LLM judge ensemble + meta-reviewer + append-only `promote.sh`), the `conducting-autonomous-experiments` SKILL.md (the method), the awareness context, an API-free end-to-end deterministic smoke that drives 3 iterations through the Phase 1 bash mechanics, and the Karpathy/`autoresearch` attribution.

**Architecture:** Pure config + markdown + deterministic shell, exactly as Phases 1–2. The promotion gate is a stand-alone sub-recipe (`steps:` shape, mirrored from `recipes/residual-adjudicator.yaml`) invoked by the Phase 2 orchestrator's `promotion-gate` stage. The judge panel reuses `behaviors/cross-vendor-judge.md` + `context/orchestrated-loop-judge-rubric.md` + the `agents/ml-paper-reviewer.md` ensemble+meta-reviewer pattern via explicit cross-vendor `provider_preferences` fallback chains (NO `class:` inside `provider_preferences` — the engine rejects it). The deterministic gate is a hermetic bash test over Phase 1 helpers; the smoke recipe is structurally validated, not executed in the gate.

**Tech Stack:** YAML recipes (validated via `amplifier tool invoke recipes operation=validate` and `bash scripts/validate-all-recipes.sh`), markdown SKILL.md (frontmatter `name:`/`description:`, mirrored from cached `skills/parallax-methodology/SKILL.md`) + awareness context, bash deterministic tests (hermetic `mktemp -d` + throwaway `git init`, modeled on Phase 1's `scripts/experiment-loop/tests/`), python3 + PyYAML for the agent/template structural checks already in the harness.

**Depends on Phase 1 (deterministic helpers) and Phase 2 (loop recipe, experiment-runner agent, /execute dispatch, bundle registration).**

---

## Important dependency facts (read before Task 10)

These are load-bearing — verify them, do not re-create what already exists:

- **`scripts/experiment-loop/promote.sh` and `scripts/experiment-loop/tests/test_promote.sh` were BUILT IN PHASE 1** (Phase 1 Tasks 8–9). Phase 3 **consumes** them in the promotion-gate recipe and the end-to-end smoke; it does NOT re-create them. Deliverable "promote.sh appends an append-only `confirmation:` block" is therefore already satisfied — Task 10 only verifies it.
- **The test harness auto-discovers tests.** `scripts/experiment-loop/tests/run_all.sh` globs `test_*.sh`, so any new `test_*.sh` file (this phase adds three) is included automatically — there is no manifest to edit. (Re-read `scripts/experiment-loop/tests/run_all.sh` from Phase 1 to confirm: it loops `for t in "$HERE"/test_*.sh`.)
- **`bundle.md` was bumped to v0.9.0 in Phase 2 (Task 7)** and the skills source was declared there. Phase 3 only ADDS the README attribution and CONFIRMS the version bump (Task 19 adds the bump ONLY if Phase 2 somehow didn't land it).
- **`recipes/autonomous-experiment-promotion-gate.yaml` is referenced by the Phase 2 orchestrator** (`recipes/autonomous-experiment-loop.yaml`'s `promotion-gate` stage calls `./autonomous-experiment-promotion-gate.yaml` with context `prereg_path`, `ledger_path`, `run_command`, `scripts_dir` and `output: promotion_result`). This phase creates it; its context keys and `promotion_result` output MUST match what the orchestrator passes.

## Conventions you MUST follow

- **Boolean context = strings.** Use `"true"`/`"false"` and `condition: "{{var}} == 'true'"` (see `recipes/_smoke-boolean-condition.yaml`).
- **No `class:` inside `provider_preferences`.** The engine rejects it (v0.8.3 schema-discovery correction). Cross-vendor judging is expressed as an explicit `{ provider:, model: }` fallback chain spanning ≥2 vendor families (mirror `recipes/orchestrated-loop-iteration.yaml:77-80`).
- **Agent short-name refs** in recipes: `research:experiment-runner`, `research:statistician`, `research:honest-critic`, `research:research-coordinator` (loader prepends `agents/`, appends `.md`).
- **All new `.sh` files** start with `#!/usr/bin/env bash`, are `chmod +x`, and are hermetic (`mktemp -d` + `trap '... ' EXIT`; their own `git init` where git is touched). Never touch the real repo's git state.
- **Commit after every task. Do NOT push.** Run all commands from repo root: `/Users/michaeljabbour/dev/amplifier-bundle-research`.

---

### Task 10: Pre-flight — confirm Phases 1 & 2 are green and `promote.sh` is present

No new files. This task verifies the foundation Phase 3 builds on.

**Step 1: Phase 1 + Phase 2 helper harness is green**

Run:
```bash
bash scripts/experiment-loop/tests/run_all.sh; echo "exit=$?"
```
Expected: `ALL EXPERIMENT-LOOP HELPER TESTS PASSED (7 files)` and `exit=0`. (7 = Phase 1's six + Phase 2's `test_experiment_runner_agent.sh`.) If not green, STOP and finish Phases 1–2.

**Step 2: Confirm `promote.sh` (Phase 1 deliverable) exists, is executable, and its test passes**

Run:
```bash
ls -l scripts/experiment-loop/promote.sh
bash scripts/experiment-loop/tests/test_promote.sh; echo "exit=$?"
```
Expected: `promote.sh` shows `-rwxr-xr-x`; the test prints `PASS: promote` and `exit=0`. (If `promote.sh` is missing, Phase 1 is incomplete — STOP and finish Phase 1; do NOT re-create it here.)

**Step 3: Confirm the harness auto-discovers tests + the recipe-validate command works**

Run:
```bash
grep -n 'for t in' scripts/experiment-loop/tests/run_all.sh
amplifier tool invoke recipes operation=validate recipe_path=recipes/autonomous-experiment-loop.yaml 2>&1 | grep -E '"status"|valid|INVALID' | head -2
```
Expected: the harness shows `for t in "$HERE"/test_*.sh` (auto-glob, no manifest to edit); the Phase 2 orchestrator recipe still reports `valid`. (No commit in this task.)

---

### Task 11: Promotion-gate sub-recipe — `recipes/autonomous-experiment-promotion-gate.yaml`

**Files:**
- Create: `recipes/autonomous-experiment-promotion-gate.yaml`

> READ `recipes/residual-adjudicator.yaml` (sub-recipe `steps:` shape, blinded-adjudication pattern) and `recipes/orchestrated-loop-iteration.yaml` (the `judge-satisfaction` step's cross-vendor `provider_preferences` fallback chain at lines 77-80, and the `@research:context/...` rubric-by-reference pattern) FIRST. Mirror their exact step grammar. The context keys + `promotion_result` output name below MUST match what the Phase 2 orchestrator passes (`recipes/autonomous-experiment-loop.yaml` `promotion-gate` stage).

**Step 1: Write the recipe to verify the validator rejects its absence (RED)**

Run (BEFORE creating the file):
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/autonomous-experiment-promotion-gate.yaml 2>&1 | tail -3
```
Expected: an error / not-found (the file does not exist yet). This is the failing state.

**Step 2: Create the recipe**

Create `recipes/autonomous-experiment-promotion-gate.yaml` with EXACTLY this content:
```yaml
# autonomous-experiment-promotion-gate.yaml — the rigor differentiator.
#
# Stand-alone sub-recipe invoked by autonomous-experiment-loop.yaml AFTER the
# loop terminates. Everything inside the loop is EXPLORATORY (a greedy search
# over a metric is overfitting-prone and multiple-comparisons-laden). This gate
# is the firewall that turns a candidate into a defensible FINDING — or honestly
# returns a null result.
#
# Flow (mirror of recipes/residual-adjudicator.yaml's steps: shape):
#   1. select kept candidates        (the running optima the loop discovered)
#   2. confirmatory re-run           (HELD-OUT seeds the loop never touched)
#   3. statistical adjudication      (tool-experiment-power + Benjamini–Hochberg)
#   4. cross-vendor judge panel      (ensemble + meta-reviewer; judgment metrics)
#   5. compose confirmation block(s) (append-only YAML for promote.sh)
#   6. apply promotion               (promote.sh, exploratory -> confirmatory)
#   7. honest-pivot review           (if nothing confirms, say so plainly)
#
# Held-out is NON-NEGOTIABLE: reusing the loop's own measurement to "confirm" is
# the canonical p-hacking trap. The gate breaks the search/validation
# entanglement. Pure orchestration over EXISTING tools — no new code.
#
# Pattern transfer (idea-level) from Andrej Karpathy's autoresearch (MIT). The
# promotion gate, n>1 variance, BH correction, and cross-vendor judge panel are
# this bundle's discipline added ON TOP of autoresearch's keep/revert loop.

name: autonomous-experiment-promotion-gate
version: 0.1.0
description: |
  Held-out promotion gate: confirmatory re-run on reserved seeds, BH-corrected
  significance, and a cross-vendor multi-LLM judge ensemble + meta-reviewer.
  Flips only candidates clearing corrected significance AND panel agreement from
  exploratory -> confirmatory (append-only, via promote.sh). If nothing
  confirms, returns an honest null result. Emits promotion_result for the parent
  loop.

context:
  prereg_path: ""                # the hash-locked pre-registration
  ledger_path: "experiments/study/ledger.yaml"
  run_command: ""                # the FROZEN measurement run_command
  scripts_dir: "scripts/experiment-loop"
  held_out_seeds: "100 101 102"  # reserved in the locked plan; loop never touched these
  alpha: 0.05                    # pre-registered confirmatory alpha
  sut_vendor: ""                 # system-under-test vendor family (for cross-vendor judge)

steps:

  - id: select-kept-candidates
    agent: research:experiment-runner
    prompt: |
      Read the append-only ledger at {{ledger_path}} and the locked
      pre-registration at {{prereg_path}}. Select the KEPT candidates on the
      final branch — the running optima the loop discovered (rows with
      decision: keep and label: exploratory that were not later reverted).

      Emit a JSON dict:
        {"candidates": [{"iteration": <int>, "commit": "<sha>",
                         "intervention": "<one-line>"}],
         "candidate_count": <int>}
    output: selection
    parse_json: true

  - id: confirmatory-rerun-held-out
    type: bash
    command: |
      set -uo pipefail
      # Re-execute the FROZEN run_command on the HELD-OUT seeds the search never
      # saw. This breaks search/validation entanglement. Output is captured for
      # the statistician + audit; the loop's own seeds are NOT reused here.
      : > .promotion_confirm_metrics.txt
      for seed in {{held_out_seeds}}; do
        echo "--- held-out seed $seed ---"
        SEED="$seed" {{run_command}} | tee -a .promotion_confirm_metrics.txt \
          || echo "RUN_FAILED held-out seed=$seed"
      done
      echo "confirmatory-rerun: done"

  - id: statistical-adjudication
    agent: research:statistician
    prompt: |
      Held-out confirmation metrics (one block per held-out seed) are in
      .promotion_confirm_metrics.txt in the working dir. Candidates:
      {{selection}}. Pre-registration: {{prereg_path}}; alpha = {{alpha}}.

      Use tool-experiment-power to evaluate each candidate's held-out effect
      against the pre-registered alpha, then apply a Benjamini–Hochberg
      correction ACROSS the number of candidates promoted (the bundle default
      multiple_comparison_correction). A candidate clears statistics ONLY if it
      passes the BH-corrected significance AND respects every guardrail tolerance.

      Emit a JSON dict:
        {"per_candidate": [{"iteration": <int>, "raw_p": <float>,
                            "bh_corrected_p": <float>, "alpha": {{alpha}},
                            "passes_corrected": "true|false",
                            "guardrails_ok": "true|false"}],
         "n_compared": <int>, "correction": "benjamini-hochberg"}
    output: stats_verdict
    parse_json: true

  - id: cross-vendor-judge-panel
    agent: research:honest-critic
    provider_preferences:
      - { provider: anthropic, model: "claude-opus-4-8" }
      - { provider: openai,    model: "gpt-5.5" }
      - { provider: google,    model: "gemini*" }
    prompt: |
      Cross-vendor multi-LLM judge panel (ensemble + meta-reviewer) for the
      held-out confirmation. Apply the rubric at
      @research:context/orchestrated-loop-judge-rubric.md and the cross-vendor
      enforcement in @research:behaviors/cross-vendor-judge.md. Use the
      ensemble + meta-reviewer aggregation pattern from
      @research:agents/ml-paper-reviewer.md (independent per-vendor verdicts,
      then a meta-reviewer reconciliation; preserve minority concerns).

      SUT vendor (exclude this family from the panel): {{sut_vendor}}.
      Candidates: {{selection}}. Statistical verdict: {{stats_verdict}}.
      Held-out metrics: .promotion_confirm_metrics.txt.

      Each vendor model judges INDEPENDENTLY, then the meta-reviewer reconciles.
      Record inter-judge agreement (Cohen's kappa). If kappa is below the
      pre-registered kappa_threshold, the metric is SUSPICIOUS — judges
      disagreeing means the metric is not trustworthy regardless of the score.

      Emit a JSON dict:
        {"per_candidate": [{"iteration": <int>,
                            "per_judge": [{"model": "...", "verdict": "promote|hold"}],
                            "meta_verdict": "promote|hold",
                            "kappa": <float>, "kappa_below_threshold": "true|false"}],
         "meta_reviewer": "<provider/model that reconciled>"}
    output: judge_verdict
    parse_json: true

  - id: compose-confirmation-blocks
    agent: research:research-coordinator
    prompt: |
      Combine the statistical verdict {{stats_verdict}} and the judge-panel
      verdict {{judge_verdict}}. A candidate is CONFIRMED iff:
        passes_corrected == "true" AND guardrails_ok == "true"
        AND meta_verdict == "promote" AND kappa_below_threshold == "false".

      For EACH confirmed candidate, build an append-only confirmation record
      matching templates/experiment-ledger.yaml's confirmation schema. Produce a
      SINGLE YAML document containing all confirmed records (one list item per
      candidate, each a top-level mapping whose only key is `confirmation`).

      Emit a JSON dict with EXACTLY these keys:
        - confirmed (string: "true" if >=1 candidate confirmed, else "false")
        - confirmation_yaml (string: the full YAML doc to append; "" if none)
        - confirmed_iterations (list of ints)
    output: confirmation
    parse_json: true

  - id: apply-promotion
    type: bash
    condition: "{{confirmation.confirmed}} == 'true'"
    command: |
      set -uo pipefail
      BLOCK=$(mktemp)
      cat > "$BLOCK" <<'PROMOTEOF'
      {{confirmation.confirmation_yaml}}
      PROMOTEOF
      bash {{scripts_dir}}/promote.sh "{{ledger_path}}" "$BLOCK" \
        "ledger: promote confirmed candidates (held-out + BH + panel)"
      rm -f "$BLOCK"

  - id: honest-pivot-review
    agent: research:honest-critic
    prompt: |
      Review the gate outcome. Confirmed iterations: {{confirmation.confirmed_iterations}}.
      Statistical verdict: {{stats_verdict}}. Judge verdict: {{judge_verdict}}.

      If NOTHING confirmed, say so plainly — the loop produced a greedy search
      result that did NOT survive held-out confirmation. Do not dress up noise;
      /draft must report a null/exploratory result (honest-pivot). If candidates
      confirmed, state the corrected significance and panel agreement honestly.

      Emit a JSON dict with EXACTLY these keys:
        - confirmed_iterations (list of ints)
        - null_result (string: "true" if nothing confirmed, else "false")
        - rationale (string)
    output: promotion_result
    parse_json: true
```

> NOTE: the `cross-vendor-judge-panel` step uses an explicit `provider:`/`model:` fallback chain (NOT `class:`) spanning Anthropic + OpenAI + Google, satisfying `behaviors/cross-vendor-judge.md`'s cross-vendor requirement with the user-specified models (`claude-opus-4-8`, `gpt-5.5`). The `{{sut_vendor}}` is excluded by the behavior's resolver at runtime.

**Step 3: Validate the recipe (GREEN)**

Run:
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/autonomous-experiment-promotion-gate.yaml 2>&1 | tail -8
```
Expected: output contains `"status": "valid"` (or `valid`). If INVALID, reconcile the step grammar against `recipes/residual-adjudicator.yaml` (a common cause: a key the engine doesn't accept on a given step type, or `class:` left in `provider_preferences`). Fix and re-run until valid.

**Step 4: Commit**

Run:
```bash
git add recipes/autonomous-experiment-promotion-gate.yaml
git commit -m "feat: add autonomous-experiment promotion-gate sub-recipe (held-out + BH + cross-vendor panel)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 12: The method — `skills/conducting-autonomous-experiments/SKILL.md`

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_skill_method.sh`
- Create: `skills/conducting-autonomous-experiments/SKILL.md`

> READ a cached SKILL.md for the exact frontmatter shape: `~/.amplifier/cache/amplifier-bundle-parallax-discovery-*/skills/parallax-methodology/SKILL.md` (frontmatter is `name:` + `description:` between `---` delimiters). The skills SOURCE was declared in `bundle.md` in Phase 2 (Task 7) — this skill is discoverable because of that. (Dependency: if `bundle.md` has no `skills:` source, Phase 2 is incomplete — STOP and finish it.)

**Step 1: Write the failing structural test (RED)**

Create `scripts/experiment-loop/tests/test_skill_method.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Structural test for skills/conducting-autonomous-experiments/SKILL.md:
#   - file exists
#   - frontmatter has name: and description:
#   - Karpathy/autoresearch (MIT) attribution line present
#   - the three judge-panel reference filenames are present
#   - the four anti-patterns are named
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SKILL="$HERE/../../../skills/conducting-autonomous-experiments/SKILL.md"
test -f "$SKILL" || { echo "FAIL: SKILL.md missing: $SKILL"; exit 1; }

grep -q "^name:" "$SKILL"        || { echo "FAIL: frontmatter missing name:"; exit 1; }
grep -q "^description:" "$SKILL" || { echo "FAIL: frontmatter missing description:"; exit 1; }

# Attribution
grep -qi "autoresearch" "$SKILL" || { echo "FAIL: missing autoresearch attribution"; exit 1; }
grep -qi "Karpathy"     "$SKILL" || { echo "FAIL: missing Karpathy attribution"; exit 1; }
grep -q  "MIT"          "$SKILL" || { echo "FAIL: missing MIT license note"; exit 1; }

# Judge-panel references (the three named assets — NOT cache-only-verify.yaml)
for ref in "cross-vendor-judge.md" "orchestrated-loop-judge-rubric.md" "ml-paper-reviewer.md"; do
  grep -q "$ref" "$SKILL" || { echo "FAIL: missing reference $ref"; exit 1; }
done
grep -q "cache-only-verify" "$SKILL" && { echo "FAIL: must NOT reference cache-only-verify"; exit 1; }

# Four anti-patterns
for ap in "n=1" "multiple-comparison" "no-hypothesis" "metric monoculture"; do
  grep -qi "$ap" "$SKILL" || { echo "FAIL: missing anti-pattern: $ap"; exit 1; }
done

echo "PASS: skill_method"
exit 0
```

**Step 2: Run to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_skill_method.sh
bash scripts/experiment-loop/tests/test_skill_method.sh; echo "exit=$?"
```
Expected: FAIL — `SKILL.md` does not exist yet, `exit=1`.

**Step 3: Create the skill**

Run:
```bash
mkdir -p skills/conducting-autonomous-experiments
```

Create `skills/conducting-autonomous-experiments/SKILL.md` with EXACTLY this content:
```markdown
---
name: conducting-autonomous-experiments
description: "The method for running the full empirical lifecycle — data collection to honest conclusion — as a tight autonomous loop against a FROZEN measurement apparatus, disciplined so the output is a defensible finding, not a hill-climb. Use during /execute when the locked pre-registration declares an experiment_loop (intervention_surface + measurement_protocol)."
---

# Conducting Autonomous Experiments

## Overview

This skill is the disciplined descendant of Andrej Karpathy's `autoresearch`
`program.md` protocol. That protocol runs a tight autonomous loop —

```
propose → run → measure → keep/revert → log → repeat
```

— against a FROZEN measurement apparatus (the agent may edit `train.py`, but
never `prepare.py` or the eval), using git as the experiment ledger. The loop is
powerful, but on its own it produces a HILL-CLIMB, not a FINDING. This skill
keeps the loop and adds the rigor organs that make its output defensible:
pre-registration hash-lock, n>1 variance, guardrail metrics, an integrity audit,
a held-out promotion gate, and a cross-vendor multi-LLM judge panel.

**Use when:** the locked pre-registration declares an `experiment_loop`.
**Don't use when:** there is no executable measurement, no intervention surface,
or the goal is a single-pass analysis (then `/execute` runs unchanged).

## The frozen apparatus (the scientific core)

Reproduce autoresearch's "edit `train.py`, never the eval" discipline through
the bundle's EXISTING sha256 pre-registration hash-lock. Four things are frozen
inside the hash-locked plan (see `templates/preregistration.yaml`'s
`experiment_loop` block):

1. **`intervention_surface`** — the files/parameters the loop MAY mutate.
2. **`measurement_protocol`** — the `run_command` + how the primary metric is
   parsed (the frozen eval). Includes the judge panel when the metric is
   LLM-judged.
3. **`primary_metric` + direction + keep/revert rule.**
4. **`guardrail_metrics` + tolerances, `stopping_rule`, `seeds`, and the
   `held_out_confirmation` set/seeds reserved for the promotion gate.**

`intervention_surface` and `measurement_protocol` MUST be disjoint — the loop may
edit the surface, never the protocol. `scripts/experiment-loop/freeze_gate.sh`
enforces this at commit time. Changing any frozen field requires a NEW
pre-registration (new hash) — never an in-loop edit. This procedurally prevents
goalpost-moving.

## The ledger rules (git is the record)

The ledger (`templates/experiment-ledger.yaml`) is append-only, one YAML item
per iteration, written by `scripts/experiment-loop/ledger_append.sh`. Rules:

- The ledger lives OUTSIDE the `intervention_surface` and is committed in its OWN
  commit, AFTER the keep/revert decision — never in the same commit as the
  intervention. This is why **a broken intervention is data**: reverting the
  intervention (`git reset --hard HEAD~1`) drops only the code change; the ledger
  row recording that failure is committed afterward and survives.
- Every row is stamped **exploratory** by default. No loop result is ever a
  conclusion; it is a candidate.
- The promotion gate APPENDS a `confirmation:` record (carrying the new label)
  rather than mutating a row in place — preserving the append-only audit trail.

## The promotion gate (the rigor differentiator)

Inside the loop everything is exploratory; a greedy search over one metric is
overfitting-prone and multiple-comparisons-laden. After the loop terminates,
`recipes/autonomous-experiment-promotion-gate.yaml` runs:

1. **Select** the kept candidates (the running optima).
2. **Confirmatory re-run** on the HELD-OUT seeds/set the loop never touched —
   the firewall against the canonical p-hacking trap.
3. **Statistical adjudication** — `statistician` + `tool-experiment-power` against
   the pre-registered alpha, with **Benjamini–Hochberg** correction across the
   candidates compared.
4. **Cross-vendor judge panel** (below) for judgment-based metrics.
5. **Verdict** — only candidates clearing corrected significance AND respecting
   guardrails AND winning panel agreement flip **exploratory → confirmatory**
   (append-only, via `promote.sh`). Everything else stays exploratory, honestly.
6. **Honest pivot** — if nothing confirms, the recipe says so plainly and
   `/draft` reports a null/exploratory result rather than dressing up noise.

## The four anti-patterns (what makes a loop a hill-climb)

autoresearch's loop has four known flaws; this skill exists to discipline each:

| Anti-pattern | The flaw | The discipline |
|---|---|---|
| **n=1 decisions** | keep/revert from a single run, no variance | run across `seeds` (n>1); `statistician` + `tool-experiment-power` compute mean + across-seed sd |
| **greedy multiple-comparisons** | a long greedy search over one metric, never corrected | the held-out promotion gate + Benjamini–Hochberg correction |
| **no-hypothesis tweaking** | changes are random tweaks, not predictions | every proposal is a mini-hypothesis: a written `rationale` + a directional `prediction` |
| **metric monoculture** | a single scalar invites silent regressions elsewhere | `guardrail_metrics` + tolerances; keep only if no guardrail regresses |

## The cross-vendor multi-LLM judge panel

Wherever the loop relies on JUDGMENT rather than a deterministic number, use a
cross-vendor multi-LLM judge panel (e.g. `anthropic/claude-opus-4-8` +
`openai/gpt-5.5`), never a single model. This reuses the bundle's existing
assets:

- `behaviors/cross-vendor-judge.md` — the enforcement gate: the judge must be
  from a DIFFERENT vendor family than the system-under-test (mitigates
  same-vendor leniency bias). Expressed as an explicit `provider:`/`model:`
  fallback chain (the schema rejects `class:` inside `provider_preferences`).
- `context/orchestrated-loop-judge-rubric.md` — the scoring rubric the judge
  applies, with hard-fail conditions.
- `agents/ml-paper-reviewer.md` — the ensemble + meta-reviewer aggregation
  pattern (independent per-vendor verdicts, then a meta-reviewer reconciliation
  that preserves minority concerns).

The panel + its models are part of the FROZEN measurement protocol, so judges
cannot be swapped mid-loop to manufacture a win. Record inter-judge agreement
(Cohen's kappa) per iteration; if kappa falls below the pre-registered
`kappa_threshold`, `tool-experiment-audit` flags the metric SUSPICIOUS — judges
disagreeing means the metric is not trustworthy regardless of the score.

## Provenance / attribution

This method is a pattern transfer (idea-level) from Andrej Karpathy's
`autoresearch` `program.md` (MIT). The GPU/PyTorch/CUDA training code is
intentionally NOT imported — only the propose/run/measure/keep-revert/log
discipline, disciplined here with this bundle's pre-registration hash-lock, n>1
variance, guardrails, integrity audit, held-out promotion gate, and cross-vendor
judge panel.
```

**Step 4: Run the test to verify it passes (GREEN)**

Run:
```bash
bash scripts/experiment-loop/tests/test_skill_method.sh; echo "exit=$?"
```
Expected: prints `PASS: skill_method` and `exit=0`.

**Step 5: Commit**

Run:
```bash
git add scripts/experiment-loop/tests/test_skill_method.sh skills/conducting-autonomous-experiments/SKILL.md
git commit -m "feat: add conducting-autonomous-experiments SKILL.md (the method) + structural test

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 13: Awareness context — `context/autonomous-loop-awareness.md`

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_awareness_context.sh`
- Create: `context/autonomous-loop-awareness.md`

> READ an existing awareness doc for tone/structure, e.g. `context/experiment-integrity-awareness.md` or `context/experiment-calibration-awareness.md`. Keep it short — "when to reach for the loop, and its honest limits."

**Step 1: Write the failing structural test (RED)**

Create `scripts/experiment-loop/tests/test_awareness_context.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Structural test for context/autonomous-loop-awareness.md — key-section grep.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DOC="$HERE/../../../context/autonomous-loop-awareness.md"
test -f "$DOC" || { echo "FAIL: awareness doc missing: $DOC"; exit 1; }

for phrase in \
  "When to reach for the loop" \
  "Honest limits" \
  "greedy search" \
  "confirmatory" \
  "intervention_surface"
do
  grep -qi "$phrase" "$DOC" || { echo "FAIL: awareness doc missing: $phrase"; exit 1; }
done

echo "PASS: awareness_context"
exit 0
```

**Step 2: Run to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_awareness_context.sh
bash scripts/experiment-loop/tests/test_awareness_context.sh; echo "exit=$?"
```
Expected: FAIL — the doc does not exist yet, `exit=1`.

**Step 3: Create the awareness doc**

Create `context/autonomous-loop-awareness.md` with EXACTLY this content:
```markdown
# Autonomous Experiment Loop — Awareness

When a locked pre-registration declares an `experiment_loop` block, `/execute`
runs the autonomous experiment loop (`recipes/autonomous-experiment-loop.yaml`)
instead of a single pass. This note says when to reach for it — and its honest
limits. The method itself lives in
`skills/conducting-autonomous-experiments/SKILL.md`.

## When to reach for the loop

Reach for the loop ONLY when ALL of these hold:

- There is an **executable measurement** — a `run_command` that emits a primary
  scalar metric (plus guardrail metrics), repeatable across seeds.
- There is a **mutable `intervention_surface`** — a file/parameter set the loop
  may edit, **disjoint** from the frozen measurement protocol.
- The question is **"which intervention moves the metric?"** — an iterative
  optimization, not a one-shot analysis.
- You have reserved a **held-out confirmation set/seeds** the search will never
  touch (required by the promotion gate).

If any of these is missing, do NOT declare an `experiment_loop`. Plans without
one run `/execute` exactly as before (single-pass), unchanged.

## Honest limits (read before trusting a loop result)

- **A loop result is a candidate, not a conclusion.** Everything inside the loop
  is labeled exploratory. A greedy search over one metric is overfitting-prone
  and multiple-comparisons-laden by construction.
- **Greedy search ≠ confirmatory result.** Only the held-out promotion gate
  (`recipes/autonomous-experiment-promotion-gate.yaml`) — confirmatory re-run on
  reserved seeds + Benjamini–Hochberg correction + cross-vendor judge panel —
  can flip a candidate from exploratory to **confirmatory**.
- **If nothing confirms, that is the finding.** The gate returns an honest null;
  `/draft` reports it as such (honest-pivot). Do not re-run the loop on the
  held-out set to "rescue" a result — that destroys the firewall.
- **The apparatus is frozen.** The loop may only edit files inside
  `intervention_surface`; changing the metric, protocol, stopping rule, seeds, or
  held-out set requires a NEW pre-registration (new hash), never an in-loop edit.

## Related

- Method: `skills/conducting-autonomous-experiments/SKILL.md`
- Engine: `recipes/autonomous-experiment-loop.yaml` (+ iteration body + gate)
- Frozen-apparatus fields: `templates/preregistration.yaml` (`experiment_loop`)
- Ledger schema: `templates/experiment-ledger.yaml`
- Judge panel: `behaviors/cross-vendor-judge.md`,
  `context/orchestrated-loop-judge-rubric.md`, `agents/ml-paper-reviewer.md`
```

**Step 4: Run the test to verify it passes (GREEN)**

Run:
```bash
bash scripts/experiment-loop/tests/test_awareness_context.sh; echo "exit=$?"
```
Expected: prints `PASS: awareness_context` and `exit=0`.

**Step 5: Commit**

Run:
```bash
git add scripts/experiment-loop/tests/test_awareness_context.sh context/autonomous-loop-awareness.md
git commit -m "feat: add autonomous-loop-awareness context + structural test

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 14: Wire `context/instructions.md` to reference the awareness doc

**Files:**
- Modify: `context/instructions.md`

> Phase 2 (Task 8) added the `experiment-runner` agent block to `context/instructions.md` but did NOT reference the awareness doc (it didn't exist yet). Add that reference now. READ `context/instructions.md` first and find the `### experiment-runner` block.

**Step 1: Add the See-also reference**

Use `edit_file`. Match the END of the Phase 2-added `experiment-runner` block (its `**Wraps:**` line):
```markdown
**Wraps:** No K-Dense skill — uses `skills/conducting-autonomous-experiments`; reuses statistician, tool-experiment-audit/power, honest-critic
```
Replace with that SAME line plus a See-also line:
```markdown
**Wraps:** No K-Dense skill — uses `skills/conducting-autonomous-experiments`; reuses statistician, tool-experiment-audit/power, honest-critic
**See also:** `context/autonomous-loop-awareness.md` (when to reach for the loop + its honest limits)
```

**Step 2: Verify the edit landed**

Run:
```bash
grep -c "autonomous-loop-awareness.md" context/instructions.md; echo "exit=$?"
```
Expected: count `≥ 1`, `exit=0`.

**Step 3: Commit**

Run:
```bash
git add context/instructions.md
git commit -m "docs: reference autonomous-loop-awareness from instructions

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 15: Smoke fixtures — deterministic `run.sh` + `intervention.txt`

**Files:**
- Create: `tests/fixtures/smoke-experiment/run.sh`
- Create: `tests/fixtures/smoke-experiment/intervention.txt`

**Step 1: Create the fixture directory + files**

Run:
```bash
mkdir -p tests/fixtures/smoke-experiment
```

Create `tests/fixtures/smoke-experiment/run.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Deterministic stand-in for a frozen measurement run_command. Emits one
# parseable primary metric line. No API, no network, no randomness — the
# end-to-end smoke needs a fixed number so keep/revert is deterministic.
echo "seed: ${SEED:-0}"
echo "primary_metric: 0.42"
```

Create `tests/fixtures/smoke-experiment/intervention.txt` with EXACTLY this content:
```text
# A file INSIDE the smoke intervention_surface. The scripted smoke edits this
# file (an in-surface change) so freeze_gate.sh PASSES; editing anything outside
# tests/fixtures/smoke-experiment/ would be rejected.
intervention-baseline
```

**Step 2: Make `run.sh` executable and verify it emits the metric line**

Run:
```bash
chmod +x tests/fixtures/smoke-experiment/run.sh
SEED=7 tests/fixtures/smoke-experiment/run.sh
```
Expected:
```
seed: 7
primary_metric: 0.42
```

**Step 3: Commit**

Run:
```bash
git add tests/fixtures/smoke-experiment/run.sh tests/fixtures/smoke-experiment/intervention.txt
git commit -m "test: add deterministic smoke-experiment fixtures (run.sh + intervention.txt)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 16: Smoke recipe — `recipes/_smoke-autonomous-experiment-loop.yaml`

**Files:**
- Create: `recipes/_smoke-autonomous-experiment-loop.yaml`

> READ `recipes/_smoke-boolean-condition.yaml` FIRST (the `_`-prefix marks it bundle-internal so `validate-all-recipes.sh` skips it; we validate it explicitly). This recipe uses bash-only steps with a SCRIPTED intervention sequence — it does NOT require the LLM `experiment-runner`. All work happens inside a self-contained `mktemp -d` so the recipe is safe to run and never touches the real repo. It exercises the Phase 1 bash mechanics (freeze_gate → decide → ledger_append) then the promotion-gate append (promote.sh). The DETERMINISTIC GATE is the bash test in Task 17; this recipe is structurally validated here.

**Step 1: Verify the validator rejects its absence (RED)**

Run (BEFORE creating the file):
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/_smoke-autonomous-experiment-loop.yaml 2>&1 | tail -3
```
Expected: an error / not-found (the file does not exist yet).

**Step 2: Create the recipe**

Create `recipes/_smoke-autonomous-experiment-loop.yaml` with EXACTLY this content:
```yaml
# Internal smoke for the autonomous experiment loop's DETERMINISTIC mechanics.
# Not for end-user invocation. The underscore prefix excludes it from
# validate-all-recipes.sh; validate it explicitly.
#
# Drives 3 SCRIPTED iterations (no LLM experiment-runner) exercising the Phase 1
# bash helpers (freeze_gate -> decide keep/revert -> ledger_append) then the
# promotion-gate append (promote.sh). Everything runs inside a self-contained
# mktemp -d git repo, so running this recipe never touches the real bundle repo.
#
# The authoritative deterministic GATE is the hermetic bash test
# scripts/experiment-loop/tests/test_smoke_end_to_end.sh (Task 17). This recipe
# is the structurally-validated, optionally-runnable companion.

name: _smoke-autonomous-experiment-loop
version: 0.1.0
description: |
  Internal smoke-test recipe driving 3 scripted iterations through the
  experiment-loop bash mechanics + the promotion-gate append, in a self-contained
  temp git repo. Bundle-internal; validated, not part of the deterministic gate.

context:
  scripts_dir: "scripts/experiment-loop"

steps:

  - id: drive-three-iterations-and-promote
    type: bash
    command: |
      set -uo pipefail
      SCRIPTS="$(pwd)/{{scripts_dir}}"
      TMP=$(mktemp -d)
      trap 'rm -rf "$TMP"' EXIT
      cd "$TMP"
      git init -q
      git config user.email t@t; git config user.name t
      mkdir -p surface experiments
      echo "frozen" > eval.txt          # outside the surface (must never change)
      echo "base"   > surface/train.txt
      git add -A; git commit -qm "baseline"
      printf 'surface/*\n' > allow.txt
      LEDGER="experiments/ledger.yaml"

      # --- iteration 1: in-surface change -> KEEP ---
      echo "iter1" >> surface/train.txt; git add -A; git commit -qm "intervention 1"
      bash "$SCRIPTS/freeze_gate.sh" allow.txt "HEAD~1 HEAD"
      printf -- '- iteration: 1\n  decision: keep\n  label: exploratory\n' > r1.txt
      bash "$SCRIPTS/decide.sh" keep
      bash "$SCRIPTS/ledger_append.sh" "$LEDGER" r1.txt "ledger: iter 1"

      # --- iteration 2: in-surface change -> REVERT ---
      echo "iter2" >> surface/train.txt; git add -A; git commit -qm "intervention 2"
      bash "$SCRIPTS/freeze_gate.sh" allow.txt "HEAD~1 HEAD"
      printf -- '- iteration: 2\n  decision: revert\n  label: exploratory\n' > r2.txt
      bash "$SCRIPTS/decide.sh" revert
      bash "$SCRIPTS/ledger_append.sh" "$LEDGER" r2.txt "ledger: iter 2"

      # --- iteration 3: in-surface change -> KEEP ---
      echo "iter3" >> surface/train.txt; git add -A; git commit -qm "intervention 3"
      bash "$SCRIPTS/freeze_gate.sh" allow.txt "HEAD~1 HEAD"
      printf -- '- iteration: 3\n  decision: keep\n  label: exploratory\n' > r3.txt
      bash "$SCRIPTS/decide.sh" keep
      bash "$SCRIPTS/ledger_append.sh" "$LEDGER" r3.txt "ledger: iter 3"

      # --- promotion gate: append a confirmation block (append-only) ---
      cat > conf.txt <<'CONFEOF'
      - confirmation:
          confirms_iteration: 3
          label: confirmatory
          meta_verdict: promote
      CONFEOF
      bash "$SCRIPTS/promote.sh" "$LEDGER" conf.txt "ledger: confirm iter 3"

      echo "smoke: 3 iterations + promotion complete"
      grep -c '^- iteration:' "$LEDGER"
```

**Step 3: Validate the recipe (GREEN)**

Run:
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/_smoke-autonomous-experiment-loop.yaml 2>&1 | tail -8
```
Expected: output contains `"status": "valid"` (or `valid`). If INVALID, reconcile the bash-step grammar against `recipes/_smoke-boolean-condition.yaml` + `recipes/cache-only-verify.yaml`. Fix and re-run until valid.

**Step 4: Commit**

Run:
```bash
git add recipes/_smoke-autonomous-experiment-loop.yaml
git commit -m "test: add internal smoke recipe for autonomous experiment loop mechanics

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 17: End-to-end deterministic smoke — `test_smoke_end_to_end.sh`

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_smoke_end_to_end.sh`

> This is the authoritative API-FREE deterministic gate. It exercises the Phase 1 helpers (`freeze_gate.sh` → `decide.sh` → `ledger_append.sh` → `promote.sh`) end-to-end in a hermetic temp git repo with a scripted 3-iteration sequence (keep, revert, keep) + a promotion append. Because the helpers already exist (Phase 1), this is an INTEGRATION assertion: it should PASS on first run. A failure means a real regression in the mechanics. The harness auto-discovers it (no manifest edit needed).

**Step 1: Write the end-to-end test**

Create `scripts/experiment-loop/tests/test_smoke_end_to_end.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# End-to-end deterministic smoke (API-FREE). Drives 3 scripted iterations through
# the Phase 1 bash mechanics + the promotion-gate append, in a hermetic temp git
# repo. Asserts:
#   - exactly 3 ledger iteration rows
#   - at least one KEEP and at least one REVERT
#   - reverts did NOT delete ledger rows (all 3 iterations survive)
#   - a confirmation block was appended (promotion gate)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SCRIPTS="$HERE/.."
FREEZE="$SCRIPTS/freeze_gate.sh"
DECIDE="$SCRIPTS/decide.sh"
APPEND="$SCRIPTS/ledger_append.sh"
PROMOTE="$SCRIPTS/promote.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t; git config user.name t
mkdir -p surface experiments
echo "frozen" > eval.txt
echo "base"   > surface/train.txt
git add -A; git commit -qm "baseline"
printf 'surface/*\n' > allow.txt
LEDGER="experiments/ledger.yaml"

# iteration 1 -> KEEP
echo "iter1" >> surface/train.txt; git add -A; git commit -qm "intervention 1"
bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1 \
  || { echo "FAIL: iter1 freeze_gate rejected an in-surface change"; exit 1; }
printf -- '- iteration: 1\n  decision: keep\n  label: exploratory\n' > r1.txt
bash "$DECIDE" keep >/dev/null
bash "$APPEND" "$LEDGER" r1.txt "ledger: iter 1" >/dev/null

# iteration 2 -> REVERT
echo "iter2" >> surface/train.txt; git add -A; git commit -qm "intervention 2"
bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1 \
  || { echo "FAIL: iter2 freeze_gate rejected an in-surface change"; exit 1; }
printf -- '- iteration: 2\n  decision: revert\n  label: exploratory\n' > r2.txt
bash "$DECIDE" revert >/dev/null            # drop the intervention FIRST
bash "$APPEND" "$LEDGER" r2.txt "ledger: iter 2" >/dev/null   # THEN log it

# iteration 3 -> KEEP
echo "iter3" >> surface/train.txt; git add -A; git commit -qm "intervention 3"
bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1 \
  || { echo "FAIL: iter3 freeze_gate rejected an in-surface change"; exit 1; }
printf -- '- iteration: 3\n  decision: keep\n  label: exploratory\n' > r3.txt
bash "$DECIDE" keep >/dev/null
bash "$APPEND" "$LEDGER" r3.txt "ledger: iter 3" >/dev/null

# promotion gate: append a confirmation block (append-only)
cat > conf.txt <<'CONFEOF'
- confirmation:
    confirms_iteration: 3
    label: confirmatory
    meta_verdict: promote
CONFEOF
bash "$PROMOTE" "$LEDGER" conf.txt "ledger: confirm iter 3" >/dev/null

# --- assertions ---
ROWS=$(grep -c '^- iteration:' "$LEDGER")
[ "$ROWS" -eq 3 ] || { echo "FAIL: expected 3 ledger rows, got $ROWS"; exit 1; }

KEEPS=$(grep -c 'decision: keep' "$LEDGER")
REVERTS=$(grep -c 'decision: revert' "$LEDGER")
[ "$KEEPS" -ge 1 ]   || { echo "FAIL: expected >=1 keep, got $KEEPS"; exit 1; }
[ "$REVERTS" -ge 1 ] || { echo "FAIL: expected >=1 revert, got $REVERTS"; exit 1; }

# reverts did NOT delete rows: all three iterations present
for n in 1 2 3; do
  grep -q "^- iteration: $n\$" "$LEDGER" \
    || { echo "FAIL: revert deleted ledger row for iteration $n"; exit 1; }
done

# confirmation block appended by the promotion gate
grep -q 'confirms_iteration: 3' "$LEDGER" \
  || { echo "FAIL: promotion confirmation block not appended"; exit 1; }

echo "PASS: smoke_end_to_end (3 rows; keeps=$KEEPS reverts=$REVERTS; confirmation appended)"
exit 0
```

**Step 2: Run the test (it exercises Phase 1 helpers — expected PASS)**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_smoke_end_to_end.sh
bash scripts/experiment-loop/tests/test_smoke_end_to_end.sh; echo "exit=$?"
```
Expected: prints `PASS: smoke_end_to_end (3 rows; keeps=2 reverts=1; confirmation appended)` and `exit=0`. If it FAILS, a Phase 1 helper has regressed — fix the helper (not the test), per its Phase 1 unit test, before continuing.

**Step 3: Commit**

Run:
```bash
git add scripts/experiment-loop/tests/test_smoke_end_to_end.sh
git commit -m "test: add API-free end-to-end smoke for experiment-loop mechanics + promotion

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 18: OPTIONAL (on-demand) — full LLM integration smoke

> **OPTIONAL. NOT part of the deterministic gate.** This task documents the on-demand procedure for exercising the REAL loop end-to-end with the LLM `experiment-runner` agent + the cross-vendor judge panel. It REQUIRES API keys and network, is non-deterministic, and is explicitly excluded from `run_all.sh` and CI. Do this only when manually validating the live wiring; there is no test file and no commit.

**Procedure (manual, requires API keys):**

1. Author a throwaway locked pre-registration whose `experiment_loop` block points `intervention_surface` at a scratch file and `measurement_protocol.run_command` at `tests/fixtures/smoke-experiment/run.sh`, with `seeds: [0,1,2]`, `stopping_rule.max_iterations: 2`, and a `held_out_confirmation.seeds: [100,101,102]`.
2. Run the real loop:
   ```bash
   amplifier tool invoke recipes operation=execute \
     recipe_path=@research:recipes/autonomous-experiment-loop.yaml \
     'context={"prereg_path":"<your-prereg>","intervention_surface_file":"<allowlist>","run_command":"tests/fixtures/smoke-experiment/run.sh","ledger_path":"experiments/smoke/ledger.yaml","seeds":"0 1 2","max_iterations":2}'
   ```
3. Expect: a `ledger.yaml` with exploratory rows, then the promotion gate either appends a `confirmation:` block (if the held-out re-run + BH correction + panel agree) or returns an honest `null_result: "true"`.

**This is a wiring check, not an assertion gate.** Do not gate any commit on it.

---

### Task 19: Attribution — README credit + confirm v0.9.0

**Files:**
- Modify: `README.md`
- (Confirm only) `bundle.md` version

> The version bump 0.8.5 → 0.9.0 and the skills source were done in Phase 2 (Task 7). This task ADDS the Karpathy/`autoresearch` (MIT) credit to `README.md` and CONFIRMS the bump. Add the bump here ONLY if Phase 2 didn't land it.

**Step 1: Confirm the Phase 2 version bump**

Run:
```bash
python3 -c "import yaml; t=open('bundle.md',encoding='utf-8').read(); d=yaml.safe_load(t.split('---')[1]); print('version:', d['bundle']['version'])"
```
Expected: `version: 0.9.0`. If it prints `0.8.5`, Phase 2's Task 7 bump is missing — apply it now with `edit_file` (`  version: 0.8.5` → `  version: 0.9.0`) and commit separately before continuing.

**Step 2: Add the README attribution**

Use `edit_file` on `README.md`. Match the existing License section anchor (lines 149-151):
```markdown
## License

MIT. Credits and lineage in [`docs/LINEAGE.md`](docs/LINEAGE.md).
```
Replace with that SAME section preceded by a new attribution note:
```markdown
## v0.9.0 (2026-05-29) — Autonomous experiment loop

Adds the autonomous experiment loop: the full empirical lifecycle (data →
analysis → honest conclusion) for any scientific experiment, run as a tight
`propose → collect → analyze → decide → log` loop against a hash-locked FROZEN
apparatus, terminating in a held-out promotion gate (confirmatory re-run +
Benjamini–Hochberg correction + cross-vendor multi-LLM judge panel). The output
is a defensible FINDING — confirmatory or honest null — not a hill-climb.

New: `skills/conducting-autonomous-experiments/SKILL.md` (the method),
`recipes/autonomous-experiment-loop.yaml` (+ iteration body + promotion gate),
`agents/experiment-runner.md` (the scientist-in-the-loop),
`templates/experiment-ledger.yaml` (append-only ledger),
`context/autonomous-loop-awareness.md`, and `scripts/experiment-loop/` helpers.
Reached via `/execute` only when the locked plan declares an `experiment_loop`;
plans without one behave exactly as before.

**Attribution.** The loop is a pattern transfer (idea-level) from Andrej
Karpathy's [`autoresearch`](https://github.com/karpathy/autoresearch)
`program.md` (MIT): `propose → run → measure → keep/revert → log` against a
frozen apparatus, with git as the experiment ledger. The GPU/PyTorch/CUDA
training code is intentionally NOT imported — only the discipline, hardened here
with pre-registration hash-lock, n>1 variance, guardrails, an integrity audit, a
held-out promotion gate, and a cross-vendor judge panel.

## License

MIT. Credits and lineage in [`docs/LINEAGE.md`](docs/LINEAGE.md).
```

**Step 3: Verify the edits landed**

Run:
```bash
grep -c "autoresearch" README.md
grep -c "v0.9.0 (2026-05-29) — Autonomous experiment loop" README.md
```
Expected: each count `≥ 1`.

**Step 4: Commit**

Run:
```bash
git add README.md
git commit -m "docs: add v0.9.0 autonomous experiment loop section + Karpathy/autoresearch attribution

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 20: Phase 3 acceptance — full gate green

**Step 1: Run the entire deterministic harness (now includes promote + skill + awareness + end-to-end smoke)**

Run:
```bash
bash scripts/experiment-loop/tests/run_all.sh; echo "exit=$?"
```
Expected output (order may vary):
```
PASS: freeze_gate
PASS: decide
PASS: ledger_append
PASS: promote
PASS: ledger_template
PASS: prereg_fields
PASS: experiment_runner_agent
PASS: skill_method
PASS: awareness_context
PASS: smoke_end_to_end (3 rows; keeps=2 reverts=1; confirmation appended)
------------------------------------------
ALL EXPERIMENT-LOOP HELPER TESTS PASSED (10 files)
exit=0
```

**Step 2: Validate BOTH new recipes (gate + internal smoke)**

Run:
```bash
for r in recipes/autonomous-experiment-promotion-gate.yaml recipes/_smoke-autonomous-experiment-loop.yaml; do
  echo "=== $r ==="
  amplifier tool invoke recipes operation=validate recipe_path="$r" 2>&1 | grep -E '"status"|valid|INVALID|error' | head -3
done
```
Expected: each prints a `valid` status.

**Step 3: Run the bundle's full recipe + reference gauntlet**

Run:
```bash
bash scripts/validate-all-recipes.sh 2>&1 | tail -6
bash scripts/check-recipe-agent-refs.sh 2>&1 | tail -4
```
Expected: `RECIPE VALIDATION: N valid, 0 invalid` (the underscore-prefixed smoke is skipped by this script; the promotion-gate recipe is included and valid) and `AGENT REFERENCE AUDIT: ... 0 unresolved` (the promotion-gate's `research:experiment-runner` / `statistician` / `honest-critic` / `research-coordinator` refs all resolve).

**Step 4: Re-run the SKILL + awareness structural checks explicitly**

Run:
```bash
bash scripts/experiment-loop/tests/test_skill_method.sh; echo "skill exit=$?"
bash scripts/experiment-loop/tests/test_awareness_context.sh; echo "awareness exit=$?"
```
Expected: both print `PASS: ...` with `exit=0`.

**Step 5: Final status check**

Run:
```bash
git status --porcelain
```
Expected: empty (all committed). If not empty, stage and commit the remainder with `chore: finalize phase 3 promotion gate + skill + smoke`.

---

## Phase 3 Done — Definition of Done

- [ ] `recipes/autonomous-experiment-promotion-gate.yaml` exists, passes `recipes validate`, and matches the context keys + `promotion_result` output the Phase 2 orchestrator passes.
- [ ] `skills/conducting-autonomous-experiments/SKILL.md` exists with valid frontmatter, the four anti-patterns, the cross-vendor judge panel referencing `cross-vendor-judge.md` + `orchestrated-loop-judge-rubric.md` + `ml-paper-reviewer.md`, and the Karpathy/`autoresearch` (MIT) attribution.
- [ ] `context/autonomous-loop-awareness.md` exists; `context/instructions.md` references it.
- [ ] `tests/fixtures/smoke-experiment/{run.sh,intervention.txt}` exist; `run.sh` is executable and emits `primary_metric: 0.42`.
- [ ] `recipes/_smoke-autonomous-experiment-loop.yaml` exists and passes `recipes validate`.
- [ ] `scripts/experiment-loop/tests/test_smoke_end_to_end.sh` asserts 3 rows, ≥1 keep + ≥1 revert, no rows deleted by reverts, and a confirmation block appended.
- [ ] `README.md` carries the v0.9.0 section + Karpathy/`autoresearch` (MIT) attribution; `bundle.md` is v0.9.0 (from Phase 2).
- [ ] `bash scripts/experiment-loop/tests/run_all.sh` exits `0` with 10 passing test files.
- [ ] `scripts/validate-all-recipes.sh` reports 0 invalid; `scripts/check-recipe-agent-refs.sh` reports 0 unresolved.
- [ ] Every task committed locally; nothing pushed.

**Phase 3 acceptance criteria:** `bash scripts/experiment-loop/tests/run_all.sh` exits 0 (now includes promote + end-to-end smoke); both new recipes pass `recipes validate`; SKILL.md + awareness context structural checks pass.

**Loop complete.** With Phases 1–3 in place, the bundle conducts the full empirical lifecycle for any scientific experiment — data → analysis → honest conclusion — and the output is a defensible finding, not a hill-climb.
