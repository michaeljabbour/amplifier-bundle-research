# Autonomous Experiment Loop — Implementation Plan, Phase 2 (Loop Engine + Agent + Dispatch)

> **Execution:** Use the subagent-driven-development workflow to implement this plan.
> **For execution:** use `/execute-plan`.

**Goal:** Wire the Phase 1 deterministic helpers into a runnable loop: a new `experiment-runner` agent (the scientist-in-the-loop), the stand-alone `autonomous-experiment-loop.yaml` recipe engine (propose → collect → analyze → decide → log), the `/execute` dispatch contract, bundle registration (+ skills source + version bump), and the instructions/routing updates.

**Architecture:** A stand-alone loop recipe (a SIBLING of `orchestrated-loop.yaml`, NOT an extension of it — resolving the design's open question). The loop body is expressed with this engine's proven while-construct, which attaches `while_condition`/`max_while_iterations`/`break_when`/`update_context` to a `type: recipe` step (exactly as `orchestrated-loop.yaml` does). Validation is structural: `recipes validate`, the bundle's own check scripts, and a frontmatter lint.

**Tech Stack:** YAML recipes (engine schema mirrored from `recipes/orchestrated-loop.yaml` + `recipes/orchestrated-loop-iteration.yaml` + `recipes/cache-only-verify.yaml`), markdown agent frontmatter (mirrored from `agents/statistician.md`), bash steps (`type: bash`), the `tool-experiment-*` modules (reused unchanged), python3 for frontmatter lint.

**Dependency:** Requires Phase 1 complete — the recipe's bash steps call `scripts/experiment-loop/{freeze_gate,decide,ledger_append}.sh` and rely on `templates/experiment-ledger.yaml` + the `experiment_loop` prereg fields. Run `bash scripts/experiment-loop/tests/run_all.sh` (must exit 0) before starting.

---

## IMPORTANT structural decision (read before Task 1)

The design's open question — *extend `orchestrated-loop.yaml` or stand alone?* — is **resolved in favor of stand-alone** (per the brainstorm "lean" and the write-plan scope boundary).

This engine attaches the while-loop to a `type: recipe` step whose `recipe:` is an **iteration body** (see `recipes/orchestrated-loop.yaml:120-141` driving `recipes/orchestrated-loop-iteration.yaml`). To mirror that proven, validating pattern, this phase creates **one additional recipe not in the original file list**: `recipes/autonomous-experiment-iteration.yaml` (the loop body). This is a deliberate, necessary addition — inlining `while_condition` on a `type: bash` step is not an attested pattern in this repo and risks failing `recipes validate`. The orchestrator recipe + iteration body together are the stand-alone engine.

So Phase 2 creates THREE recipes:
- `recipes/autonomous-experiment-loop.yaml` — orchestrator (provenance pre-gate → while-loop → hand-off to promotion gate).
- `recipes/autonomous-experiment-iteration.yaml` — the loop body (one iteration: propose → freeze-gate → collect → analyze → audit → decide → log).
- (Phase 3 adds `recipes/autonomous-experiment-promotion-gate.yaml`.)

---

## Conventions you MUST follow

- **Boolean context = strings.** Use `"true"`/`"false"` strings for context booleans and conditions, e.g. `condition: "{{flag}} == 'true'"` (see `recipes/_smoke-boolean-condition.yaml` and the v0.8.3 note: the engine REJECTS `class:` inside `provider_preferences` entries — use explicit `{ provider:, model: }` fallback chains).
- **Agent short-name refs.** In recipes and `bundle.md`, reference agents as `research:experiment-runner` (loader prepends `agents/`, appends `.md`). Do NOT write the path or extension.
- **Agent frontmatter shape.** `meta.name` + `meta.description` (with an `<example>` block) + `model_role:`, then the body, ending with `@foundation:context/shared/common-agent-base.md`. Mirror `agents/statistician.md` exactly.
- Commit after every task. Do NOT push.
- Run all commands from repo root: `/Users/michaeljabbour/dev/amplifier-bundle-research`.

---

### Task 1: Pre-flight — confirm Phase 1 is green

**Step 1: Run the Phase 1 harness**

Run:
```bash
bash scripts/experiment-loop/tests/run_all.sh; echo "exit=$?"
```
Expected: `ALL EXPERIMENT-LOOP HELPER TESTS PASSED (6 files)`, `exit=0`. If not, STOP and finish Phase 1.

**Step 2: Confirm the recipe validate command works on an existing recipe**

Run:
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/orchestrated-loop.yaml 2>&1 | tail -5
```
Expected: output containing `"status": "valid"` (or `valid`). This proves the validate command + environment are usable. (No commit in this task.)

---

### Task 2: `experiment-runner` agent — write the failing frontmatter-lint test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_experiment_runner_agent.sh`

> READ `agents/statistician.md` (lines 1–16) first to copy the EXACT frontmatter shape (`meta:` → `name:` / `description:` with an `<example>`, then `model_role:`).

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_experiment_runner_agent.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Frontmatter lint for agents/experiment-runner.md:
#   - file exists
#   - YAML frontmatter (between the first two '---' lines) parses
#   - meta.name == experiment-runner
#   - model_role == reasoning
#   - body ends by including the shared agent base
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
AGENT="$HERE/../../../agents/experiment-runner.md"
test -f "$AGENT" || { echo "FAIL: agent missing: $AGENT"; exit 1; }

python3 - "$AGENT" <<'PY' || exit 1
import sys, yaml
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
parts = text.split("---")
if len(parts) < 3:
    print("FAIL: no YAML frontmatter delimited by ---"); sys.exit(1)
fm = yaml.safe_load(parts[1])
meta = (fm or {}).get("meta", {})
if meta.get("name") != "experiment-runner":
    print(f"FAIL: meta.name != experiment-runner (got {meta.get('name')!r})"); sys.exit(1)
if fm.get("model_role") != "reasoning":
    print(f"FAIL: model_role != reasoning (got {fm.get('model_role')!r})"); sys.exit(1)
if "common-agent-base.md" not in text:
    print("FAIL: body does not include common-agent-base.md"); sys.exit(1)
print("frontmatter-ok")
PY

echo "PASS: experiment_runner_agent"
exit 0
```

**Step 2: Run to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_experiment_runner_agent.sh
bash scripts/experiment-loop/tests/test_experiment_runner_agent.sh; echo "exit=$?"
```
Expected: FAIL — `agents/experiment-runner.md` does not exist, `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_experiment_runner_agent.sh
git commit -m "test: add failing frontmatter lint for experiment-runner agent

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 3: `experiment-runner` agent — create it, make the lint pass

**Files:**
- Create: `agents/experiment-runner.md`

**Step 1: Write the agent**

Create `agents/experiment-runner.md` with EXACTLY this content:
```markdown
---
meta:
  name: experiment-runner
  description: |
    Use during /execute when the locked pre-registration declares an `experiment_loop` (intervention_surface + measurement_protocol). The scientist-in-the-loop for the autonomous experiment loop: given the frozen apparatus and the ledger-so-far, it proposes the NEXT intervention as a mini-hypothesis (a written rationale + a directional prediction), edits ONLY files inside the frozen intervention_surface, and after analysis applies the pre-registered keep/revert rule. It never touches the measurement protocol, stopping rule, or held-out set (all frozen).

    Distinct from `research-coordinator` (which routes modes) and `statistician` (which selects tests and computes power): experiment-runner makes the scientific judgment call of WHAT to try next and WHETHER to keep it, within the hash-locked apparatus.

    <example>
    User: [/execute on a plan whose preregistration declares experiment_loop with intervention_surface: src/train.py]
    Agent reads the ledger (iterations 1-6), proposes "increase MLP width 512->768" with rationale "capacity-bound; predict primary improves >= 0.5%", edits only src/train.py, commits. After the recipe collects metrics across seeds and the statistician + audit report back, the agent applies the keep/revert rule (keep iff primary improves beyond noise AND no guardrail regresses) and emits the decision for the ledger.
    </example>
model_role: reasoning
---

# Agent: experiment-runner

**Invoked by recipes:** `autonomous-experiment-loop.yaml` / `autonomous-experiment-iteration.yaml` (during `/execute`)
**Reused rigor organs:** `preregistration-reviewer` (apparatus lock), `statistician` + `tool-experiment-power` (variance), `tool-experiment-audit` (integrity), `honest-critic` / `honest-pivot` (promotion gate)

---

## Role

Be the scientist inside the autonomous loop. Each iteration, read the frozen pre-registration and the append-only ledger, then do exactly two jobs:

1. **PROPOSE** the next intervention as a mini-hypothesis — never a random tweak. Every proposal carries a written `rationale` and a directional `prediction`. Edit ONLY files matched by the frozen `intervention_surface`. Commit the change (git is the keep/revert substrate).
2. **DECIDE** keep or revert, strictly by the pre-registered `keep_revert_rule`, AFTER the recipe has collected metrics across seeds and the statistician + audit have reported.

You are the judgment in "recipe orchestrates, agent decides, tools compute, git records." You do NOT control flow, compute statistics, or write the ledger row — the recipe does those.

## Hard constraints (frozen apparatus)

- **Never edit the measurement protocol, stopping rule, seeds, or held-out confirmation set.** They are hash-locked. If achieving your idea would require changing them, STOP and say so — that requires a NEW pre-registration.
- **Never edit a file outside `intervention_surface`.** The recipe runs `freeze_gate.sh` after your commit; an out-of-surface change is rejected and you are re-prompted. Stay inside the surface.
- **Every change is a prediction.** No rationale + no directional prediction = not a valid proposal.
- **Keep/revert is mechanical.** Apply the pre-registered rule exactly; do not invent new acceptance criteria mid-loop. A crash, an integrity FAIL/SUSPICIOUS, or a quorum of failed seeds is an automatic `revert`.
- **Everything is exploratory by default.** No loop result is a conclusion. Confirmation happens only at the promotion gate.

## Behavior contract

Reads: the locked pre-registration (`experiment_loop` block) + the ledger-so-far (`experiments/<study>/ledger.yaml`) + the latest iteration's parsed metrics / statistician output / audit verdict (on the DECIDE call).
Writes: on PROPOSE — a code edit inside the surface + a commit + a JSON proposal (`intervention`, `rationale`, `prediction`); on DECIDE — a JSON decision (`decision`, `decision_reason`).
Does not: run the command, compute statistics, write the ledger, or change any frozen field.

## Output contract — PROPOSE

```json
{
  "intervention": "<one-line description of the change>",
  "rationale": "<why you expect this to help; the mechanism>",
  "prediction": "<directional, e.g. 'primary down >= 0.5%'>",
  "files_touched": ["<paths, all inside intervention_surface>"],
  "commit_subject": "<git subject for the intervention commit>"
}
```

## Output contract — DECIDE

```json
{
  "decision": "keep | revert",
  "decision_reason": "<cite the pre-registered rule + the observed numbers>",
  "prediction_outcome": "confirmed | disconfirmed | inconclusive"
}
```

## Proposal discipline (what makes a good next intervention)

- Prefer interventions whose predicted effect is *separable* from the last one (don't confound two changes in one commit — one hypothesis per iteration).
- Read the ledger for plateaus: if recent iterations all reverted, change the KIND of intervention, not the magnitude.
- State the mechanism, not just the direction. "Wider MLP -> more capacity -> lower val loss" beats "make it bigger."
- When the metric is LLM-judged, remember the judge panel is frozen; do not propose changes that only game one judge.

## Attribution

The loop method this agent serves is a pattern transfer (idea-level) from Andrej Karpathy's `autoresearch` (`program.md`, MIT). The GPU/PyTorch training code is intentionally NOT imported — only the propose/run/measure/keep-revert/log discipline, disciplined here with this bundle's pre-registration, variance (n>1), guardrails, and promotion gate.

@foundation:context/shared/common-agent-base.md
```

**Step 2: Run the lint to verify it passes**

Run:
```bash
bash scripts/experiment-loop/tests/test_experiment_runner_agent.sh; echo "exit=$?"
```
Expected: prints `frontmatter-ok` then `PASS: experiment_runner_agent`, `exit=0`.

**Step 3: Commit**

Run:
```bash
git add agents/experiment-runner.md
git commit -m "feat: add experiment-runner agent (scientist-in-the-loop)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 4: Iteration body recipe — create `autonomous-experiment-iteration.yaml`

**Files:**
- Create: `recipes/autonomous-experiment-iteration.yaml`

> READ `recipes/orchestrated-loop-iteration.yaml` first (it is the canonical iteration-body shape: top-level `name`/`version`/`description`/`context`/`steps`, with `type: recipe`, `type: bash`, `agent:`, `condition:`, `output:`, `parse_json:`). Mirror its step grammar exactly. Note the bash-step shape from `recipes/cache-only-verify.yaml` (`type: bash` + `command: |`).

**Step 1: Write the iteration recipe**

Create `recipes/autonomous-experiment-iteration.yaml` with EXACTLY this content:
```yaml
# autonomous-experiment-iteration.yaml — ONE iteration of the autonomous
# experiment loop. Spawned by autonomous-experiment-loop.yaml's while step in an
# isolated sub-session. Receives only the inputs listed in `context:`; does NOT
# inherit parent loop state.
#
# Pattern transfer (idea-level) from Andrej Karpathy's autoresearch program.md
# (MIT): propose -> run -> measure -> keep/revert -> log. Disciplined with this
# bundle's pre-registration, n>1 variance, guardrails, and integrity audit.
#
# Boundary: recipe orchestrates, agent (experiment-runner) decides, tools
# compute, git records. Mirror of recipes/orchestrated-loop-iteration.yaml.

name: autonomous-experiment-iteration
version: 0.1.0
description: |
  Single iteration: PROPOSE (experiment-runner) -> FREEZE-GATE (bash) ->
  COLLECT (bash run_command across seeds) -> ANALYZE (statistician +
  tool-experiment-power) -> AUDIT (tool-experiment-audit) -> DECIDE
  (experiment-runner applies the pre-registered keep/revert rule) -> LOG
  (decide.sh then ledger_append.sh, ledger committed separately). Emits a JSON
  dict the parent loop's update_context parses.

context:
  prereg_path: ""               # path to the hash-locked pre-registration
  ledger_path: ""               # experiments/<study>/ledger.yaml (outside surface)
  intervention_surface_file: "" # allowlist file for freeze_gate.sh
  run_command: ""               # the frozen measurement run_command
  seeds: "0 1 2"                # space-separated seeds for the bash loop
  iteration_index: 0
  scripts_dir: "scripts/experiment-loop"

steps:

  - id: propose-intervention
    agent: research:experiment-runner
    prompt: |
      Read the locked pre-registration at {{prereg_path}} and the ledger-so-far
      at {{ledger_path}}. Propose the NEXT intervention as a mini-hypothesis.
      Edit ONLY files inside the frozen intervention_surface, then commit.

      Emit the PROPOSE JSON contract:
        {"intervention": "...", "rationale": "...", "prediction": "...",
         "files_touched": ["..."], "commit_subject": "..."}
    output: proposal
    parse_json: true

  - id: freeze-gate
    type: bash
    command: |
      bash {{scripts_dir}}/freeze_gate.sh "{{intervention_surface_file}}" "HEAD~1 HEAD"

  - id: collect-across-seeds
    type: bash
    command: |
      set -uo pipefail
      : > .loop_run_metrics.txt
      for seed in {{seeds}}; do
        echo "--- seed $seed ---"
        SEED="$seed" {{run_command}} | tee -a .loop_run_metrics.txt || echo "RUN_FAILED seed=$seed"
      done
      echo "collect: done"

  - id: analyze-variance
    agent: research:statistician
    prompt: |
      The loop ran the frozen run_command across seeds {{seeds}}. The captured
      stdout (one block per seed) is in .loop_run_metrics.txt in the working dir.
      Parse the primary metric and each guardrail metric per seed. Report
      mean + across-seed sd for the primary (n>1), and per-guardrail mean vs
      tolerance. Pre-registration: {{prereg_path}}.

      Emit a JSON dict:
        {"primary": {"name": "...", "values": [...], "mean": 0.0, "sd": 0.0},
         "guardrails": [{"name": "...", "mean": 0.0, "tolerance": "...", "regressed": false}]}
    output: analysis
    parse_json: true

  - id: audit-integrity
    type: bash
    command: |
      amplifier tool invoke tool-experiment-audit operation=audit \
        path="$(dirname "{{ledger_path}}")" 2>&1 | tail -20 || \
        echo '{"audit_verdict": "ERROR"}'

  - id: decide-keep-or-revert
    agent: research:experiment-runner
    prompt: |
      Apply the pre-registered keep_revert_rule from {{prereg_path}}.
      Proposal: {{proposal}}
      Analysis (per-seed primary + guardrails): {{analysis}}
      Integrity audit output is in the previous step's stdout.

      Rule reminder: keep IFF the primary improves beyond noise AND no guardrail
      regresses past tolerance AND the audit verdict is PASS. A crash, a
      FAIL/SUSPICIOUS audit, or a quorum of failed seeds is an automatic revert.

      Emit the DECIDE JSON contract:
        {"decision": "keep|revert", "decision_reason": "...",
         "prediction_outcome": "confirmed|disconfirmed|inconclusive"}
    output: decision
    parse_json: true

  - id: apply-decision
    type: bash
    command: |
      bash {{scripts_dir}}/decide.sh "{{decision.decision}}"

  - id: write-ledger-row
    type: bash
    command: |
      set -uo pipefail
      ROW=$(mktemp)
      cat > "$ROW" <<ROWEOF
      - iteration: {{iteration_index}}
        intervention: "{{proposal.intervention}}"
        rationale: "{{proposal.rationale}}"
        prediction: "{{proposal.prediction}}"
        decision: {{decision.decision}}
        decision_reason: "{{decision.decision_reason}}"
        label: exploratory
        timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      ROWEOF
      bash {{scripts_dir}}/ledger_append.sh "{{ledger_path}}" "$ROW" "ledger: iteration {{iteration_index}}"
      rm -f "$ROW"

  - id: emit-iteration-summary
    agent: research:research-coordinator
    prompt: |
      Summarize this iteration for the parent loop. Proposal: {{proposal}}.
      Decision: {{decision}}. Analysis: {{analysis}}.

      Emit a JSON dict with EXACTLY these keys:
        - decision (string: "keep" or "revert")
        - kept_improvement (string: "true" or "false")
        - best_primary_so_far (number or null)
        - should_stop (string: "true" or "false")  # true iff patience exhausted
    output: iteration_summary
    parse_json: true
```

**Step 2: Validate the recipe**

Run:
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/autonomous-experiment-iteration.yaml 2>&1 | tail -8
```
Expected: output contains `"status": "valid"` (or `valid`). If INVALID, re-read `recipes/orchestrated-loop-iteration.yaml` and reconcile the exact step grammar (a common cause: a key the engine doesn't accept on a given step type). Fix and re-run until valid.

**Step 3: Commit**

Run:
```bash
git add recipes/autonomous-experiment-iteration.yaml
git commit -m "feat: add autonomous-experiment-iteration loop body recipe

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 5: Orchestrator recipe — create `autonomous-experiment-loop.yaml`

**Files:**
- Create: `recipes/autonomous-experiment-loop.yaml`

> READ `recipes/orchestrated-loop.yaml` first — copy its `stages:` grammar and the EXACT while-step shape (lines 120-141): `type: recipe` + `recipe:` + `context:` + `output:` + `parse_json:` + `while_condition:` + `max_while_iterations:` + `break_when:` + `update_context:`. Also note the `pre-registration` stage with an `approval:` block — we reuse that shape for the provenance hard-gate.

**Step 1: Write the orchestrator recipe**

Create `recipes/autonomous-experiment-loop.yaml` with EXACTLY this content:
```yaml
# autonomous-experiment-loop.yaml — the autonomous experiment loop engine.
#
# Stand-alone SIBLING of orchestrated-loop.yaml (NOT an extension): this
# optimizes a pre-registered scalar metric over interventions, whereas
# orchestrated-loop adjudicates residuals. Standing alone lets it own its own
# resumable ledger state (tool-experiment-resume reconciles partial ledgers).
#
# Invoked by /execute ONLY when the locked pre-registration declares an
# `experiment_loop` block (see modes/execute.md Dispatch contract). Plans
# without one never reach this recipe and behave exactly as today.
#
# Pattern transfer (idea-level) from Andrej Karpathy's autoresearch (MIT):
# propose -> run -> measure -> keep/revert -> log, against a FROZEN apparatus,
# with git as the experiment ledger. Disciplined here with pre-registration
# hash-lock, n>1 variance, guardrails, an integrity audit, and a promotion gate.
#
# Flow:
#   1. provenance-pre-gate  (hard stop if any input data file is untracked)
#   2. experiment-loop      (while-loop over autonomous-experiment-iteration.yaml)
#   3. promotion-gate       (held-out confirmation; flips exploratory->confirmatory)

name: autonomous-experiment-loop
version: 0.1.0
description: |
  Autonomous experiment loop: propose -> collect -> analyze -> decide -> log,
  against a hash-locked frozen apparatus, terminating in a held-out promotion
  gate. The output is a defensible FINDING (confirmatory or honest null), not a
  hill-climb. Stand-alone sibling of orchestrated-loop.yaml.

context:
  prereg_path: ""                 # required: the hash-locked pre-registration
  ledger_path: "experiments/study/ledger.yaml"
  intervention_surface_file: ""   # required: allowlist file for freeze_gate.sh
  run_command: ""                 # required: the frozen measurement run_command
  experiment_script: ""           # script whose data refs the provenance gate audits
  seeds: "0 1 2"
  max_iterations: 10
  scripts_dir: "scripts/experiment-loop"

  # Loop state (mutated via update_context in the while step)
  should_stop: "false"
  iteration_index: 0

stages:

  - name: provenance-pre-gate
    approval:
      required: true
      timeout: 0
      default: deny
      prompt: |
        Autonomous experiment loop — launch gate

        Pre-registration: {{prereg_path}}
        Intervention surface allowlist: {{intervention_surface_file}}
        Ledger (outside the surface, committed separately): {{ledger_path}}
        Max iterations: {{max_iterations}}   Seeds: {{seeds}}

        Before iteration 1, all input data files must be git-tracked.
        Approve to run the provenance hard-gate and begin / Deny to revise.
    steps:
      - id: data-provenance-hard-gate
        type: bash
        command: |
          set -uo pipefail
          if [ -n "{{experiment_script}}" ]; then
            amplifier tool invoke tool-experiment-provenance-check \
              operation=pre-experiment-gate \
              script_path="{{experiment_script}}" \
              repo_path="$(pwd)"
          else
            echo "provenance: no experiment_script given; skipping AST gate" >&2
            echo "provenance-pre-gate: OK (no script)"
          fi

  - name: experiment-loop
    steps:
      - id: run-one-iteration
        type: recipe
        recipe: ./autonomous-experiment-iteration.yaml
        context:
          prereg_path: "{{prereg_path}}"
          ledger_path: "{{ledger_path}}"
          intervention_surface_file: "{{intervention_surface_file}}"
          run_command: "{{run_command}}"
          seeds: "{{seeds}}"
          iteration_index: "{{iteration_index}}"
          scripts_dir: "{{scripts_dir}}"
        output: iteration_result
        parse_json: true
        while_condition: "{{should_stop}} != 'true'"
        max_while_iterations: 10
        break_when: "{{should_stop}} == 'true'"
        update_context:
          should_stop: "{{iteration_result.iteration_summary.should_stop}}"

  - name: promotion-gate
    steps:
      - id: run-promotion-gate
        type: recipe
        recipe: ./autonomous-experiment-promotion-gate.yaml
        context:
          prereg_path: "{{prereg_path}}"
          ledger_path: "{{ledger_path}}"
          run_command: "{{run_command}}"
          scripts_dir: "{{scripts_dir}}"
        output: promotion_result
        parse_json: true
```

> NOTE: the `promotion-gate` stage references `./autonomous-experiment-promotion-gate.yaml`, which is created in **Phase 3**. The orchestrator still VALIDATES now (validation checks this recipe's own schema, not the existence of referenced sub-recipes — exactly as `orchestrated-loop.yaml` references its siblings). The end-to-end smoke that actually executes the chain is in Phase 3.

**Step 2: Validate the recipe**

Run:
```bash
amplifier tool invoke recipes operation=validate recipe_path=recipes/autonomous-experiment-loop.yaml 2>&1 | tail -8
```
Expected: output contains `"status": "valid"` (or `valid`). If INVALID, reconcile the while-step grammar against `recipes/orchestrated-loop.yaml:120-141`. Fix and re-run until valid.

**Step 3: Commit**

Run:
```bash
git add recipes/autonomous-experiment-loop.yaml
git commit -m "feat: add autonomous-experiment-loop orchestrator recipe (stand-alone)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 6: `/execute` dispatch contract

**Files:**
- Modify: `modes/execute.md`

> READ `modes/execute.md` first. The frontmatter already lists `recipes`, `bash`, `delegate`, `load_skill` in `tools.safe` (lines 5–18) — no tool changes needed. You are adding ONE new documentation section that defines the dispatch behavior. Insert it right after the `## Contract` section (after line 39, before `## Reproducibility requirements` at line 41).

**Step 1: Insert the dispatch section**

Use `edit_file`. Match this existing anchor (the end of the Contract section + the start of the next):
```markdown
**Exit condition:** analysis complete, results summary produced, any deviations flagged and logged.

## Reproducibility requirements
```
Replace it with:
```markdown
**Exit condition:** analysis complete, results summary produced, any deviations flagged and logged.

## Dispatch contract — autonomous experiment loop

`/execute` inspects the locked pre-registration for an `experiment_loop` block (see `templates/preregistration.yaml`):

- **`experiment_loop` ABSENT (default):** `/execute` behaves exactly as today — single-pass, producing `execution-log.yaml` / `evidence-log.yaml` as described below. Observable output is unchanged. This is the backward-compatible path.
- **`experiment_loop` PRESENT:** `/execute` invokes `recipes/autonomous-experiment-loop.yaml`, passing `prereg_path`, `intervention_surface_file` (the allowlist derived from `experiment_loop.intervention_surface`), `run_command` (from `experiment_loop.measurement_protocol.run_command`), `seeds`, `ledger_path`, and `max_iterations` (from `experiment_loop.stopping_rule`). The loop produces an append-only `ledger.yaml` instead of a single-pass log, and terminates in the promotion gate. `max_iterations: 1` is a degenerate single-iteration loop (it still runs the loop code path and emits `ledger.yaml`) — NOT the legacy single-pass path.

No new mode is added; the loop is reached purely through this dispatch. The apparatus (intervention surface, measurement protocol, stopping rule, seeds, held-out set) is frozen in the hash-locked plan — `/execute` never edits it, and the loop may only mutate files inside `intervention_surface` (enforced by `scripts/experiment-loop/freeze_gate.sh`). See `context/autonomous-loop-awareness.md` and `skills/conducting-autonomous-experiments/SKILL.md`.

## Reproducibility requirements
```

**Step 2: Verify the edit landed**

Run:
```bash
grep -n "Dispatch contract — autonomous experiment loop" modes/execute.md; echo "exit=$?"
grep -c "experiment_loop" modes/execute.md
```
Expected: the section header matches (`exit=0`); `experiment_loop` appears at least 4 times.

**Step 3: Commit**

Run:
```bash
git add modes/execute.md
git commit -m "feat: add experiment-loop dispatch contract to /execute mode

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 7: Register the agent + skills source + version bump in `bundle.md`

**Files:**
- Modify: `bundle.md`

> READ `bundle.md` first (134 lines). Three edits: (a) bump `version: 0.8.5` → `0.9.0`; (b) add `experiment-runner` to `agents.include`; (c) declare a skills source so `skills/conducting-autonomous-experiments/SKILL.md` is discoverable. This bundle has no skills source yet — model it on how `tools:` are wired (path-based, pointing at this bundle's own dirs). Skills are consumed via `load_skill` (already in `/execute` and agent tool lists).

**Step 1a: Bump the version**

Use `edit_file`:
- old: `  version: 0.8.5`
- new: `  version: 0.9.0`

**Step 1b: Add the agent to the include list**

Use `edit_file`. Match the last AI-Scientist agent entry (lines 48–49):
```yaml
    - research:literature-scout          # gene-transferred from AI-Scientist (agentic Semantic Scholar novelty search)
    - research:idea-generator            # gene-transferred from AI-Scientist (3-axis Interestingness x Feasibility x Novelty + reflection + archive injection)
```
Replace with that SAME pair plus the new entry:
```yaml
    - research:literature-scout          # gene-transferred from AI-Scientist (agentic Semantic Scholar novelty search)
    - research:idea-generator            # gene-transferred from AI-Scientist (3-axis Interestingness x Feasibility x Novelty + reflection + archive injection)
    # v0.9.0 addition (autonomous experiment loop):
    - research:experiment-runner         # scientist-in-the-loop: proposes interventions + applies keep/revert
```

**Step 1c: Declare the skills source**

Use `edit_file`. Match the END of the `tools:` block and the closing frontmatter `---` (lines 100–102):
```yaml
  - path: modules/tool-experiment-block-hypothesis
    mount: amplifier_research_block_hypothesis:mount
---
```
Replace with:
```yaml
  - path: modules/tool-experiment-block-hypothesis
    mount: amplifier_research_block_hypothesis:mount

# --------------------------------------------------------------------------
# Skills — owned, file-discoverable SKILL.md units (v0.9.0). This bundle's
# first owned skill is conducting-autonomous-experiments (the method behind the
# autonomous experiment loop). Skills load lazily via the load_skill tool, which
# is already in the /execute mode and agent tool lists.
# --------------------------------------------------------------------------
skills:
  - path: skills
---
```

> If `recipes validate` / bundle load (Step 2) reports the `skills:` key shape is wrong for this engine, READ the foundation bundle guide for the exact skills-source key (search the foundation cache for `skills:` in a `bundle.md`), and adjust to the attested shape. The intent is fixed (make `skills/` discoverable); the exact key may differ.

**Step 2: Verify bundle.md still parses and references resolve**

Run:
```bash
python3 -c "import yaml; t=open('bundle.md',encoding='utf-8').read(); fm=t.split('---')[1]; d=yaml.safe_load(fm); print('version:', d['bundle']['version']); print('experiment-runner in agents:', 'research:experiment-runner' in d['agents']['include']); print('skills key present:', 'skills' in d)"
bash scripts/check-recipe-agent-refs.sh 2>&1 | tail -4
bash scripts/check-agent-collisions.sh 2>&1 | tail -3
```
Expected:
- `version: 0.9.0`
- `experiment-runner in agents: True`
- `skills key present: True`
- recipe→agent audit: `0 unresolved` (the new `research:experiment-runner` refs in the two new recipes now resolve to `agents/experiment-runner.md`).
- collision audit: `No collisions involving amplifier-bundle-research`.

**Step 3: Commit**

Run:
```bash
git add bundle.md
git commit -m "feat: register experiment-runner + skills source, bump to v0.9.0

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 8: Update `context/instructions.md` (agent list + recipes table + judge defaults)

**Files:**
- Modify: `context/instructions.md`

> READ `context/instructions.md` first. Three additions: (a) an `experiment-runner` entry in the agent guidance; (b) an `autonomous-experiment-loop` row in the Recipes table; (c) two rows in the Defaults table for the cross-vendor judge panel + kappa threshold.

**Step 1a: Add the agent entry**

Use `edit_file`. Match the `research-coordinator` agent block (lines 63–66):
```markdown
### research-coordinator
**When invoked:** Recipe execution, cross-mode transitions
**What it does:** Orchestrates agent routing, enforces honest-pivot, manages state across modes
**Wraps:** No specific K-Dense skill — coordinates other agents
```
Replace with that SAME block plus:
```markdown
### research-coordinator
**When invoked:** Recipe execution, cross-mode transitions
**What it does:** Orchestrates agent routing, enforces honest-pivot, manages state across modes
**Wraps:** No specific K-Dense skill — coordinates other agents

### experiment-runner
**When invoked:** `/execute` when the locked plan declares an `experiment_loop` (autonomous experiment loop)
**What it does:** The scientist-in-the-loop — proposes the next intervention as a mini-hypothesis (rationale + directional prediction) inside the frozen intervention surface, then applies the pre-registered keep/revert rule after analysis
**Wraps:** No K-Dense skill — uses `skills/conducting-autonomous-experiments`; reuses statistician, tool-experiment-audit/power, honest-critic
```

**Step 1b: Add the recipes table row**

Use `edit_file`. Match the `paperbanana-figure.yaml` table row (line 167):
```markdown
| `paperbanana-figure.yaml` | Multi-stage figure generation with approval gates |
```
Replace with:
```markdown
| `paperbanana-figure.yaml` | Multi-stage figure generation with approval gates |
| `autonomous-experiment-loop.yaml` | Autonomous experiment loop (propose → collect → analyze → decide → log) against a frozen apparatus, terminating in a held-out promotion gate. Reached via `/execute` when the locked plan declares an `experiment_loop`. Stand-alone sibling of `orchestrated-loop.yaml`. |
```

**Step 1c: Add the defaults rows**

Use `edit_file`. Match the `figure_style` defaults row (line 204):
```markdown
| `figure_style` | `publication` | Wraps `scientific-schematics` defaults; PaperBanana veto rules still apply |
```
Replace with:
```markdown
| `figure_style` | `publication` | Wraps `scientific-schematics` defaults; PaperBanana veto rules still apply |
| `judge_panel` | cross-vendor, 2–3 models + meta-reviewer | Judgment-based metrics and the promotion-gate verdict use a cross-vendor multi-LLM judge panel (e.g. `anthropic/claude-opus-4-8` + `openai/gpt-5.5`), never a single model. Pinned in the locked plan's `measurement_protocol.judge_panel` for reproducibility. Enforced via `behaviors/cross-vendor-judge.md`. |
| `judge_kappa_threshold` | `0.6` | Inter-judge Cohen's κ floor; below it, `tool-experiment-audit` flags the metric SUSPICIOUS (judges disagreeing means the metric isn't trustworthy). Hash-locked per study in `measurement_protocol.judge_panel.kappa_threshold`. |
```

**Step 2: Verify the edits landed**

Run:
```bash
grep -c "experiment-runner" context/instructions.md
grep -c "autonomous-experiment-loop" context/instructions.md
grep -c "judge_kappa_threshold" context/instructions.md
```
Expected: each count ≥ 1.

**Step 3: Commit**

Run:
```bash
git add context/instructions.md
git commit -m "docs: add experiment-runner, loop recipe, and judge-panel defaults to instructions

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 9: Phase 2 acceptance — recipes validate + bundle integrity + Phase 1 still green

**Step 1: Validate BOTH new recipes**

Run:
```bash
for r in recipes/autonomous-experiment-iteration.yaml recipes/autonomous-experiment-loop.yaml; do
  echo "=== $r ==="
  amplifier tool invoke recipes operation=validate recipe_path="$r" 2>&1 | grep -E '"status"|valid|INVALID|error' | head -3
done
```
Expected: each prints a `valid` status.

**Step 2: Run the bundle's own validation gauntlet**

Run:
```bash
bash scripts/validate-all-recipes.sh 2>&1 | tail -6
bash scripts/check-recipe-agent-refs.sh 2>&1 | tail -4
```
Expected: `RECIPE VALIDATION: N valid, 0 invalid` and `AGENT REFERENCE AUDIT: ... 0 unresolved`.

**Step 3: Re-run the Phase 1 deterministic harness (must still be green)**

Run:
```bash
bash scripts/experiment-loop/tests/run_all.sh; echo "exit=$?"
```
Expected: `ALL EXPERIMENT-LOOP HELPER TESTS PASSED (7 files)` — note Phase 2 added `test_experiment_runner_agent.sh`, so the count is now 7. `exit=0`.

**Step 4: Final status check**

Run:
```bash
git status --porcelain
```
Expected: empty (all committed). If not, commit the remainder with `chore: finalize phase 2 loop engine`.

---

## Phase 2 Done — Definition of Done

- [ ] `agents/experiment-runner.md` exists, passes the frontmatter lint, and `model_role: reasoning`.
- [ ] `recipes/autonomous-experiment-iteration.yaml` and `recipes/autonomous-experiment-loop.yaml` both pass `recipes validate`.
- [ ] `modes/execute.md` documents the `experiment_loop` dispatch contract (absent = unchanged; present = invoke the loop).
- [ ] `bundle.md` is v0.9.0, includes `research:experiment-runner`, and declares a skills source.
- [ ] `context/instructions.md` lists the agent, the recipe, and the judge-panel + κ defaults.
- [ ] `scripts/check-recipe-agent-refs.sh` reports 0 unresolved; `scripts/validate-all-recipes.sh` reports 0 invalid.
- [ ] `bash scripts/experiment-loop/tests/run_all.sh` exits 0 (7 files).
- [ ] Every task committed; nothing pushed.

**Next:** Phase 3 adds the promotion-gate sub-recipe (held-out confirmation + BH correction + cross-vendor judge ensemble + meta-reviewer + append-only `promote.sh`), the SKILL.md method doc, the awareness context, the README/attribution, and the end-to-end API-free smoke that drives 3 iterations through the bash mechanics.
