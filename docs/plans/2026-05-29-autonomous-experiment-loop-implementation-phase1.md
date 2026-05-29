# Autonomous Experiment Loop — Implementation Plan, Phase 1 (Deterministic Mechanics + Schemas)

> **Execution:** Use the subagent-driven-development workflow to implement this plan.
> **For execution:** use `/execute-plan`.

**Goal:** Build and test (TDD) the deterministic shell helpers and YAML schemas that the autonomous experiment loop stands on — the freeze gate, the keep/revert decision, the append-only ledger, the promotion append, the ledger template, and the pre-registration frozen-apparatus fields — with a self-contained, API-free test harness.

**Architecture:** Pure-bash helper scripts under `scripts/experiment-loop/` plus two YAML schema artifacts (`templates/experiment-ledger.yaml`, additions to `templates/preregistration.yaml`). Every git-touching helper is tested inside a throwaway temp git repo so tests are hermetic. No new Python module. No API calls.

**Tech Stack:** bash (target the system's bash 3.2 — no `mapfile`, no associative arrays), git, python3 + PyYAML (already installed, `yaml` 6.0.3) for the YAML structural test.

**Dependency:** This is the first phase. Phases 2 and 3 depend on the helpers and schemas built here. Nothing here depends on later phases.

**Scope note (v1):** This phase is fully deterministic and requires NO API key. The cross-vendor judge panel is declared as *schema fields* here (Task 8) but its live execution is built in Phase 3.

---

## Conventions you MUST follow

- **Boolean context convention:** elsewhere in this bundle, recipe context booleans are strings `"true"`/`"false"` (see `recipes/_smoke-boolean-condition.yaml`). Not needed in Phase 1 but keep it in mind.
- **All new `.sh` files must be executable** (`chmod +x`) and start with `#!/usr/bin/env bash`.
- **Hermetic tests only:** every test creates its own `mktemp -d` working dir (and its own `git init` repo where git is involved) and removes it via `trap '... ' EXIT`. Never touch the real repo's git state.
- **Commit after every task.** Do NOT push (push is `/finish`).
- Run all commands from the repo root: `/Users/michaeljabbour/dev/amplifier-bundle-research` unless told otherwise.

---

### Task 1: Create the experiment-loop directory + test harness skeleton

**Files:**
- Create: `scripts/experiment-loop/tests/run_all.sh`

**Step 1: Create the directories**

Run:
```bash
mkdir -p scripts/experiment-loop/tests
```

**Step 2: Write the harness**

Create `scripts/experiment-loop/tests/run_all.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Deterministic test harness for the experiment-loop shell helpers.
# Runs every test_*.sh in this directory; exits nonzero if any fails.
# Requires NO API key and NO network.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
fail=0
ran=0
for t in "$HERE"/test_*.sh; do
  [ -f "$t" ] || continue
  ran=$((ran + 1))
  if bash "$t"; then
    :
  else
    echo "  ^ FAILED: $(basename "$t")"
    fail=$((fail + 1))
  fi
done
echo "------------------------------------------"
if [ "$ran" -eq 0 ]; then
  echo "NO TESTS FOUND in $HERE"
  exit 1
fi
if [ "$fail" -eq 0 ]; then
  echo "ALL EXPERIMENT-LOOP HELPER TESTS PASSED ($ran files)"
  exit 0
fi
echo "$fail of $ran TEST FILE(S) FAILED"
exit 1
```

**Step 3: Make it executable and run it (verify it fails — no tests yet)**

Run:
```bash
chmod +x scripts/experiment-loop/tests/run_all.sh
bash scripts/experiment-loop/tests/run_all.sh; echo "exit=$?"
```
Expected: prints `NO TESTS FOUND ...` and `exit=1`. (Good — the harness correctly refuses to pass with zero tests.)

**Step 4: Commit**

Run:
```bash
git add scripts/experiment-loop/tests/run_all.sh
git commit -m "test: add experiment-loop deterministic test harness skeleton

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 2: `freeze_gate.sh` — write the failing test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_freeze_gate.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_freeze_gate.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Hermetic test for freeze_gate.sh — the frozen-apparatus enforcement gate.
# It must PASS when changed files are inside the intervention_surface allowlist
# and FAIL (nonzero) when any changed file is outside it.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
GATE="$HERE/../freeze_gate.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t; git config user.name t
mkdir -p src
echo "base"   > src/train.py
echo "frozen" > eval.py
git add -A; git commit -qm "baseline"

# Allowlist permits only files under src/
printf 'src/*\n' > allow.txt

# Case 1: in-surface change -> gate must PASS (exit 0)
echo "tweak" >> src/train.py
git add -A; git commit -qm "in-surface change"
if ! bash "$GATE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
  echo "FAIL: in-surface change was rejected"; exit 1
fi

# Case 2: out-of-surface change -> gate must FAIL (nonzero)
echo "tamper" >> eval.py
git add -A; git commit -qm "out-of-surface change"
if bash "$GATE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
  echo "FAIL: out-of-surface change was allowed"; exit 1
fi

echo "PASS: freeze_gate"
exit 0
```

**Step 2: Run the test to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_freeze_gate.sh
bash scripts/experiment-loop/tests/test_freeze_gate.sh; echo "exit=$?"
```
Expected: FAIL — the script `freeze_gate.sh` does not exist yet, so `bash "$GATE"` errors. The first `if ! bash ...` sees nonzero and prints `FAIL: in-surface change was rejected`, `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_freeze_gate.sh
git commit -m "test: add failing test for freeze_gate.sh

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 3: `freeze_gate.sh` — minimal implementation, make it pass

**Files:**
- Create: `scripts/experiment-loop/freeze_gate.sh`

**Step 1: Write the implementation**

Create `scripts/experiment-loop/freeze_gate.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# freeze_gate.sh — reject any changed file outside the frozen intervention surface.
#
# Reproduces autoresearch's "agent may edit train.py, never prepare.py/eval"
# discipline. The intervention_surface allowlist is FROZEN in the hash-locked
# pre-registration; this gate enforces it at commit time.
#
# Usage: freeze_gate.sh <allowlist_file> [diff_spec]
#   <allowlist_file>  one allowlist pattern per line (shell glob ok). Blank
#                     lines and lines starting with '#' are ignored.
#   [diff_spec]       passed verbatim to `git diff --name-only`
#                     (default: "HEAD~1 HEAD" — the most recent commit).
#
# Exit 0 if every changed file matches an allowlist pattern; exit 1 if any file
# is outside the surface; exit 2 on usage/IO error.
set -uo pipefail

allowlist="${1:?usage: freeze_gate.sh <allowlist_file> [diff_spec]}"
diff_spec="${2:-HEAD~1 HEAD}"

if [ ! -f "$allowlist" ]; then
  echo "freeze_gate: allowlist not found: $allowlist" >&2
  exit 2
fi

# Collect allowlist patterns (skip blanks + comments).
patterns=""
while IFS= read -r line; do
  case "$line" in
    ""|\#*) continue ;;
  esac
  patterns="$patterns
$line"
done < "$allowlist"

# shellcheck disable=SC2086
changed=$(git diff --name-only $diff_spec)

violations=0
for f in $changed; do
  allowed=0
  for p in $patterns; do
    # In bash `case`, '*' matches '/', so "src/*" covers nested paths too.
    # shellcheck disable=SC2254
    case "$f" in
      $p) allowed=1; break ;;
    esac
  done
  if [ "$allowed" -eq 0 ]; then
    echo "freeze_gate: OUT-OF-SURFACE change: $f" >&2
    violations=$((violations + 1))
  fi
done

if [ "$violations" -gt 0 ]; then
  echo "freeze_gate: FAIL ($violations file(s) outside intervention surface)" >&2
  exit 1
fi
echo "freeze_gate: OK"
exit 0
```

**Step 2: Make executable and run the test to verify it passes**

Run:
```bash
chmod +x scripts/experiment-loop/freeze_gate.sh
bash scripts/experiment-loop/tests/test_freeze_gate.sh; echo "exit=$?"
```
Expected: prints `PASS: freeze_gate` and `exit=0`.

**Step 3: Commit**

Run:
```bash
git add scripts/experiment-loop/freeze_gate.sh
git commit -m "feat: add freeze_gate.sh intervention-surface enforcement

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 4: `decide.sh` — write the failing test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_decide.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_decide.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Hermetic test for decide.sh — applies keep/revert to the intervention commit.
#   keep   -> commit stays
#   revert -> `git reset --hard HEAD~1`, working tree clean
#   invalid -> exit 2
# decide.sh must NEVER touch the ledger (proven indirectly here: nothing else
# in the tree changes).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DECIDE="$HERE/../decide.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t; git config user.name t
echo "base" > f.txt; git add -A; git commit -qm "baseline"
BASE=$(git rev-parse HEAD)
echo "intervention" >> f.txt; git add -A; git commit -qm "intervention"

# keep -> commit must remain (HEAD != BASE)
bash "$DECIDE" keep >/dev/null
if [ "$(git rev-parse HEAD)" = "$BASE" ]; then
  echo "FAIL: keep dropped the commit"; exit 1
fi

# revert -> HEAD back to BASE, tree clean
bash "$DECIDE" revert >/dev/null
if [ "$(git rev-parse HEAD)" != "$BASE" ]; then
  echo "FAIL: revert did not reset to baseline"; exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "FAIL: revert left a dirty tree"; exit 1
fi

# invalid -> exit 2
bash "$DECIDE" bogus >/dev/null 2>&1
if [ "$?" -ne 2 ]; then
  echo "FAIL: invalid decision did not exit 2"; exit 1
fi

echo "PASS: decide"
exit 0
```

**Step 2: Run the test to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_decide.sh
bash scripts/experiment-loop/tests/test_decide.sh; echo "exit=$?"
```
Expected: FAIL (`decide.sh` not yet created; `keep` branch can't keep the commit), `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_decide.sh
git commit -m "test: add failing test for decide.sh

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 5: `decide.sh` — minimal implementation, make it pass

**Files:**
- Create: `scripts/experiment-loop/decide.sh`

**Step 1: Write the implementation**

Create `scripts/experiment-loop/decide.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# decide.sh — apply a pre-registered keep/revert decision to the most recent
# intervention commit.
#
#   keep   -> leave the intervention commit in place (no-op).
#   revert -> `git reset --hard HEAD~1`, dropping the intervention commit.
#
# This NEVER touches the ledger: the ledger lives OUTSIDE intervention_surface
# and is appended + committed SEPARATELY, AFTER this decision (see
# ledger_append.sh). That is why "a broken intervention is data": reverting the
# code change does not erase the ledger row that records the failure.
#
# Usage: decide.sh <keep|revert>
# Exit 0 on keep/revert; exit 2 on invalid argument.
set -uo pipefail

decision="${1:?usage: decide.sh <keep|revert>}"

case "$decision" in
  keep)
    echo "decide: keep (intervention retained)"
    exit 0
    ;;
  revert)
    git reset --hard HEAD~1
    echo "decide: revert (intervention commit dropped)"
    exit 0
    ;;
  *)
    echo "decide: invalid decision '$decision' (want keep|revert)" >&2
    exit 2
    ;;
esac
```

**Step 2: Make executable and run the test to verify it passes**

Run:
```bash
chmod +x scripts/experiment-loop/decide.sh
bash scripts/experiment-loop/tests/test_decide.sh; echo "exit=$?"
```
Expected: prints `PASS: decide` and `exit=0`.

**Step 3: Commit**

Run:
```bash
git add scripts/experiment-loop/decide.sh
git commit -m "feat: add decide.sh keep/revert helper

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 6: `ledger_append.sh` — write the failing test (proves the survive-revert invariant)

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_ledger_append.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_ledger_append.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Hermetic test for ledger_append.sh — appends a row to the ledger and commits
# the ledger BY ITSELF (separate commit), AFTER the keep/revert decision.
#
# Core invariant under test: a reverted intervention must NOT delete ledger
# rows. We append row1, then make + REVERT an intervention, then append row2,
# and assert BOTH rows survive.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
APPEND="$HERE/../ledger_append.sh"
DECIDE="$HERE/../decide.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t; git config user.name t
mkdir -p experiments src
echo "base" > src/train.py; git add -A; git commit -qm "baseline"

LEDGER="experiments/ledger.yaml"

# Row 1
printf -- '- iteration: 1\n  decision: keep\n' > row1.txt
bash "$APPEND" "$LEDGER" row1.txt "ledger: iter 1" >/dev/null
test -f "$LEDGER" || { echo "FAIL: ledger not created"; exit 1; }
grep -q "iteration: 1" "$LEDGER" || { echo "FAIL: row1 missing"; exit 1; }

# Intervention that gets REVERTED
echo "tweak" >> src/train.py; git add -A; git commit -qm "intervention"
printf -- '- iteration: 2\n  decision: revert\n' > row2.txt
bash "$DECIDE" revert >/dev/null              # drop the intervention commit FIRST
bash "$APPEND" "$LEDGER" row2.txt "ledger: iter 2" >/dev/null  # THEN log it

# Both rows must survive the revert
grep -q "iteration: 1" "$LEDGER" || { echo "FAIL: revert deleted row1"; exit 1; }
grep -q "iteration: 2" "$LEDGER" || { echo "FAIL: row2 missing"; exit 1; }

# The ledger commit must be its own commit (separate from any intervention)
SUBJECT=$(git log -1 --pretty=%s)
case "$SUBJECT" in
  ledger:*) : ;;
  *) echo "FAIL: last commit is not a separate ledger commit ($SUBJECT)"; exit 1 ;;
esac

echo "PASS: ledger_append"
exit 0
```

**Step 2: Run the test to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_ledger_append.sh
bash scripts/experiment-loop/tests/test_ledger_append.sh; echo "exit=$?"
```
Expected: FAIL (`ledger_append.sh` not created; ledger never created), `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_ledger_append.sh
git commit -m "test: add failing test for ledger_append.sh (survive-revert invariant)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 7: `ledger_append.sh` — minimal implementation, make it pass

**Files:**
- Create: `scripts/experiment-loop/ledger_append.sh`

**Step 1: Write the implementation**

Create `scripts/experiment-loop/ledger_append.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# ledger_append.sh — append one iteration row to the experiment ledger, then
# commit the ledger BY ITSELF (its own commit), AFTER the keep/revert decision.
#
# The ledger lives OUTSIDE the intervention_surface and is committed separately,
# so a reverted intervention (git reset --hard HEAD~1) never deletes ledger
# rows. This is the mechanism behind "a broken intervention is data, not a stop."
#
# Usage: ledger_append.sh <ledger_file> <row_file> [commit_msg]
# Exit 0 on success; exit 2 on usage/IO error.
set -uo pipefail

ledger="${1:?usage: ledger_append.sh <ledger_file> <row_file> [commit_msg]}"
row="${2:?missing <row_file>}"
msg="${3:-ledger: append iteration row}"

if [ ! -f "$row" ]; then
  echo "ledger_append: row file not found: $row" >&2
  exit 2
fi

# Create the ledger with a header if it does not yet exist.
if [ ! -f "$ledger" ]; then
  printf '# experiment ledger (append-only). See templates/experiment-ledger.yaml\n' > "$ledger"
fi

cat "$row" >> "$ledger"

git add "$ledger"
git commit -m "$msg" -- "$ledger" >/dev/null
echo "ledger_append: appended row to $ledger and committed it separately"
exit 0
```

**Step 2: Make executable and run the test to verify it passes**

Run:
```bash
chmod +x scripts/experiment-loop/ledger_append.sh
bash scripts/experiment-loop/tests/test_ledger_append.sh; echo "exit=$?"
```
Expected: prints `PASS: ledger_append` and `exit=0`.

**Step 3: Commit**

Run:
```bash
git add scripts/experiment-loop/ledger_append.sh
git commit -m "feat: add ledger_append.sh append-only ledger writer

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 8: `promote.sh` — write the failing test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_promote.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_promote.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Hermetic test for promote.sh — the promotion gate's append-only label flip.
# It must:
#   - APPEND a confirmation block (never edit the original row in place)
#   - leave the original "label: exploratory" line intact
#   - REFUSE a block that lacks a 'confirmation:' key (exit 3)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PROMOTE="$HERE/../promote.sh"
APPEND="$HERE/../ledger_append.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t; git config user.name t
mkdir -p experiments
echo "base" > f.txt; git add -A; git commit -qm "baseline"
LEDGER="experiments/ledger.yaml"

printf -- '- iteration: 7\n  decision: keep\n  label: exploratory\n' > row.txt
bash "$APPEND" "$LEDGER" row.txt "ledger: iter 7" >/dev/null

# Valid confirmation block -> appended
cat > conf.txt <<'EOF'
- confirmation:
    confirms_iteration: 7
    label: confirmatory
    meta_verdict: promote
EOF
bash "$PROMOTE" "$LEDGER" conf.txt "ledger: confirm iter 7" >/dev/null
grep -q "confirms_iteration: 7" "$LEDGER" || { echo "FAIL: confirmation not appended"; exit 1; }
# original exploratory label NOT mutated in place (append-only audit property)
grep -q "label: exploratory" "$LEDGER" || { echo "FAIL: original row was mutated"; exit 1; }

# Invalid block (no 'confirmation:' key) -> refused, exit 3
printf 'garbage: true\n' > bad.txt
bash "$PROMOTE" "$LEDGER" bad.txt >/dev/null 2>&1
if [ "$?" -ne 3 ]; then echo "FAIL: bad block not refused with exit 3"; exit 1; fi

echo "PASS: promote"
exit 0
```

**Step 2: Run the test to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_promote.sh
bash scripts/experiment-loop/tests/test_promote.sh; echo "exit=$?"
```
Expected: FAIL (`promote.sh` not created), `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_promote.sh
git commit -m "test: add failing test for promote.sh

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 9: `promote.sh` — minimal implementation, make it pass

**Files:**
- Create: `scripts/experiment-loop/promote.sh`

**Step 1: Write the implementation**

Create `scripts/experiment-loop/promote.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# promote.sh — promotion-gate label flip, append-only.
#
# When the promotion gate confirms a candidate (held-out re-run + corrected
# significance + cross-vendor judge agreement), it APPENDS a confirmation record
# that references the iteration being promoted, then commits the ledger
# separately. It NEVER edits the original row's label in place — that would break
# the ledger's append-only audit property.
#
# Usage: promote.sh <ledger_file> <confirmation_block_file> [commit_msg]
# Exit 0 on success; 2 on usage/IO error; 3 if the block is not a confirmation.
set -uo pipefail

ledger="${1:?usage: promote.sh <ledger_file> <confirmation_block_file> [commit_msg]}"
block="${2:?missing <confirmation_block_file>}"
msg="${3:-ledger: append confirmation block}"

if [ ! -f "$ledger" ]; then
  echo "promote: ledger not found: $ledger" >&2
  exit 2
fi
if [ ! -f "$block" ]; then
  echo "promote: confirmation block not found: $block" >&2
  exit 2
fi

# Guard: refuse anything that is not a confirmation record. Keeps append-only honest.
if ! grep -q 'confirmation:' "$block"; then
  echo "promote: block missing 'confirmation:' key — refusing" >&2
  exit 3
fi

cat "$block" >> "$ledger"
git add "$ledger"
git commit -m "$msg" -- "$ledger" >/dev/null
echo "promote: appended confirmation block to $ledger"
exit 0
```

**Step 2: Make executable and run the test to verify it passes**

Run:
```bash
chmod +x scripts/experiment-loop/promote.sh
bash scripts/experiment-loop/tests/test_promote.sh; echo "exit=$?"
```
Expected: prints `PASS: promote` and `exit=0`.

**Step 3: Commit**

Run:
```bash
git add scripts/experiment-loop/promote.sh
git commit -m "feat: add promote.sh append-only confirmation writer

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 10: Ledger template — write the failing structural test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_ledger_template.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_ledger_template.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Structural test: templates/experiment-ledger.yaml must be valid YAML (via
# PyYAML if available, else a key-presence grep fallback).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
TEMPLATE="$HERE/../../../templates/experiment-ledger.yaml"
test -f "$TEMPLATE" || { echo "FAIL: template missing: $TEMPLATE"; exit 1; }

if python3 -c 'import yaml' >/dev/null 2>&1; then
  python3 -c "import yaml; yaml.safe_load(open('$TEMPLATE')); print('yaml-parse-ok')" \
    || { echo "FAIL: template is not valid YAML"; exit 1; }
else
  for key in "iteration:" "prereg_hash:" "intervention:" "primary_metric:" "decision:" "label:"; do
    grep -q "$key" "$TEMPLATE" || { echo "FAIL: template missing key $key"; exit 1; }
  done
  echo "grep-structural-ok"
fi
echo "PASS: ledger_template"
exit 0
```

**Step 2: Run to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_ledger_template.sh
bash scripts/experiment-loop/tests/test_ledger_template.sh; echo "exit=$?"
```
Expected: FAIL — `templates/experiment-ledger.yaml` does not exist yet, `exit=1`.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_ledger_template.sh
git commit -m "test: add failing structural test for experiment-ledger template

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 11: Ledger template — create it, make the test pass

**Files:**
- Create: `templates/experiment-ledger.yaml`

> Before writing, READ `templates/preregistration.yaml` and `templates/evidence-log.yaml` to match the bundle's template comment style (a banner header explaining purpose + when it is written). The ledger must `yaml.safe_load` cleanly — keep the example row's values real (numbers/strings), no `<placeholder>` tokens inside the example list.

**Step 1: Write the template**

Create `templates/experiment-ledger.yaml` with EXACTLY this content:
```yaml
# ==========================================================================
# EXPERIMENT LEDGER TEMPLATE
# ==========================================================================
# The disciplined, append-only descendant of autoresearch's results.tsv
# (Andrej Karpathy, MIT). One YAML list ITEM per loop iteration, appended by
# scripts/experiment-loop/ledger_append.sh — never edited in place.
#
# Written/owned by: recipes/autonomous-experiment-loop.yaml during /execute.
# Location: the study's working dir, e.g. experiments/<study>/ledger.yaml.
#           The ledger is git-tracked but lives OUTSIDE the intervention_surface,
#           and is committed in its OWN commit AFTER each keep/revert decision,
#           so a reverted intervention never deletes ledger rows.
#
# This file ships the SCHEMA + one worked example. It does not mandate a path.
# The promotion gate APPENDS a confirmation record (see the second list item
# below) rather than mutating a row's label in place.
# ==========================================================================

# --- Example iteration row (exploratory by default) -----------------------
- iteration: 7
  prereg_hash: "sha256:abc123"          # binds this row to the frozen apparatus
  commit: "a1b2c3d"                       # the kept/reverted intervention commit
  intervention: "increase MLP width 512->768"
  rationale: "capacity-bound; predict primary improves"
  prediction: "primary down >= 0.5%"
  seeds: [0, 1, 2]
  primary_metric:
    name: val_bpb
    values: [0.812, 0.809, 0.814]
    mean: 0.8117
    sd: 0.0025
  guardrail_metrics:
    - name: peak_vram_mb
      mean: 38120
      tolerance: "<= 40000"
      regressed: false
  judge_agreement:                        # present only when metric is LLM-judged
    kappa: null                           # Cohen's kappa across the judge panel
    kappa_threshold: 0.6                  # below this -> audit verdict SUSPICIOUS
  decision: keep                          # keep | revert
  decision_reason: "primary improved beyond 2x sd; no guardrail regression"
  label: exploratory                      # exploratory by default
  audit_verdict: PASS                     # from tool-experiment-audit: PASS|FAIL|SUSPICIOUS|ERROR
  artifacts: ["run.log", "loss_curve.png"]
  timestamp: "2026-05-29T07:30:00Z"

# --- Example confirmation record (APPENDED by the promotion gate) ----------
# The gate never rewrites the row above; it appends this, carrying the new label.
- confirmation:
    confirms_iteration: 7
    label: confirmatory
    held_out_seeds: [100, 101, 102]
    corrected_significance:
      test: paired
      alpha: 0.05
      correction: benjamini-hochberg
      passed: true
    judge_panel_verdict:
      per_judge:
        - { model: "claude-opus-4-8", verdict: promote }
        - { model: "gpt-5.5", verdict: promote }
      meta_reviewer: "gpt-5.5"
      meta_verdict: promote
      kappa: 0.81
    timestamp: "2026-05-29T09:00:00Z"
```

**Step 2: Run the test to verify it passes**

Run:
```bash
bash scripts/experiment-loop/tests/test_ledger_template.sh; echo "exit=$?"
```
Expected: prints `yaml-parse-ok` then `PASS: ledger_template`, `exit=0`.

**Step 3: Commit**

Run:
```bash
git add templates/experiment-ledger.yaml
git commit -m "feat: add experiment-ledger template (append-only schema)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 12: Pre-registration frozen-apparatus fields — write the failing structural test

**Files:**
- Create (test): `scripts/experiment-loop/tests/test_prereg_fields.sh`

**Step 1: Write the failing test**

Create `scripts/experiment-loop/tests/test_prereg_fields.sh` with EXACTLY this content:
```bash
#!/usr/bin/env bash
# Structural test: templates/preregistration.yaml must declare the frozen-
# apparatus + judge-panel + stopping-rule fields the loop hash-locks.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PREREG="$HERE/../../../templates/preregistration.yaml"
test -f "$PREREG" || { echo "FAIL: prereg missing: $PREREG"; exit 1; }

# Field-presence assertions (grep-based: the template uses <placeholder> tokens
# elsewhere, so we assert keys, not a full YAML parse).
for key in \
  intervention_surface \
  measurement_protocol \
  judge_panel \
  meta_reviewer \
  kappa_threshold \
  primary_metric \
  guardrail_metrics \
  stopping_rule \
  max_iterations \
  patience \
  budget \
  seeds \
  held_out_confirmation
do
  grep -q "$key" "$PREREG" || { echo "FAIL: prereg missing field: $key"; exit 1; }
done

echo "PASS: prereg_fields"
exit 0
```

**Step 2: Run to verify it fails**

Run:
```bash
chmod +x scripts/experiment-loop/tests/test_prereg_fields.sh
bash scripts/experiment-loop/tests/test_prereg_fields.sh; echo "exit=$?"
```
Expected: FAIL — the new fields are not in `templates/preregistration.yaml` yet, `exit=1` with a `FAIL: prereg missing field: intervention_surface` message.

**Step 3: Commit the test**

Run:
```bash
git add scripts/experiment-loop/tests/test_prereg_fields.sh
git commit -m "test: add failing field-presence test for prereg frozen apparatus

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 13: Pre-registration frozen-apparatus fields — add them, make the test pass

**Files:**
- Modify: `templates/preregistration.yaml` (insert a new block before the `# Self-witnessing hash` banner, i.e. before line 110 `# ----` / `sha256:` section)

> READ `templates/preregistration.yaml` first (113 lines). You are INSERTING a new section; do not delete existing content. The insertion point is immediately AFTER the `amendments: []` block (line 108) and BEFORE the `# Self-witnessing hash` banner (line ~110), so the new frozen-apparatus fields are inside the hash-locked body.

**Step 1: Make the edit**

Use `edit_file` to insert the new section. Match this existing anchor (lines 105–108):
```yaml
# --------------------------------------------------------------------------
# Amendment log — timestamped additions only, never deletions
# --------------------------------------------------------------------------
amendments: []   # appended to via /plan --amend, never edited in place
```
Replace it with that SAME block followed by the new frozen-apparatus section:
```yaml
# --------------------------------------------------------------------------
# Amendment log — timestamped additions only, never deletions
# --------------------------------------------------------------------------
amendments: []   # appended to via /plan --amend, never edited in place

# --------------------------------------------------------------------------
# Autonomous experiment loop — FROZEN APPARATUS (hash-locked, never in-loop)
# --------------------------------------------------------------------------
# Present ONLY when this study runs the autonomous-experiment-loop. If absent,
# /execute behaves exactly as today (single-pass). See
# context/autonomous-loop-awareness.md and
# skills/conducting-autonomous-experiments/SKILL.md.
#
# Discipline: intervention_surface and measurement_protocol MUST be disjoint
# (the loop may edit the surface; it may NEVER edit the measurement protocol).
# Changing any field below requires a NEW pre-registration (new hash).
experiment_loop:
  intervention_surface:           # files/globs the loop MAY mutate (~ train.py)
    - <path or glob, e.g. src/train.py>
  measurement_protocol:           # the FROZEN eval (~ prepare.py + eval)
    run_command: <executable command emitting the metric lines>
    primary_metric_parse: <how the primary scalar is parsed from stdout>
    judge_panel:                  # required only when the metric is LLM-judged
      enabled: false
      models:                     # cross-vendor (>=2 families); never single-model
        - <provider/model, e.g. anthropic/claude-opus-4-8>
        - <provider/model, e.g. openai/gpt-5.5>
      meta_reviewer: <provider/model that reconciles the ensemble>
      kappa_threshold: 0.6        # inter-judge Cohen's kappa floor; below -> SUSPICIOUS
  primary_metric:
    name: <metric name, e.g. val_bpb>
    direction: <minimize | maximize>
    keep_revert_rule: |
      keep iff the primary improves beyond noise (e.g. > 2x across-seed sd)
      AND no guardrail regresses past its tolerance; else revert.
  guardrail_metrics:
    - name: <metric name, e.g. peak_vram_mb>
      tolerance: <e.g. "<= 40000">
  stopping_rule:
    max_iterations: <int; 1 = degenerate single-iteration loop>
    patience: <int; stop after N iterations with no kept improvement>
    budget: <per-run wall-clock / token budget>
  seeds: [0, 1, 2]                # search seeds (n>1 fixes autoresearch's n=1)
  held_out_confirmation:          # reserved for the promotion gate; loop never touches
    seeds: [100, 101, 102]
    set: <held-out data/config the search never sees>
```

**Step 2: Run the test to verify it passes**

Run:
```bash
bash scripts/experiment-loop/tests/test_prereg_fields.sh; echo "exit=$?"
```
Expected: prints `PASS: prereg_fields` and `exit=0`.

**Step 3: Sanity-check the whole prereg still reads as a document**

Run:
```bash
python3 -c "import yaml; d=yaml.safe_load(open('templates/preregistration.yaml')); print('experiment_loop present:', 'experiment_loop' in d)" 2>&1 || echo "NOTE: prereg uses <placeholder> tokens; a parse error here is pre-existing and acceptable — the grep test is authoritative."
```
Expected: either `experiment_loop present: True`, OR the NOTE line (pre-existing placeholder tokens can make full parse loose). Either outcome is acceptable; the Task 12 grep test is the gate.

**Step 4: Commit**

Run:
```bash
git add templates/preregistration.yaml
git commit -m "feat: add frozen-apparatus + judge-panel fields to preregistration template

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 14: `preregistration-reviewer` checklist item

**Files:**
- Modify: `agents/preregistration-reviewer.md`

> READ `agents/preregistration-reviewer.md` fully first. Find the reviewer's checklist / review-criteria section (a numbered or bulleted list of what it verifies). Add ONE new item; do not restructure the file.

**Step 1: Add the checklist item**

Use `edit_file` to add this exact bullet to the reviewer's checklist (place it as the final item in the existing checklist list, matching the surrounding bullet style):
```
- **Intervention surface and measurement protocol are disjoint and frozen.** If the plan declares `experiment_loop`, verify `intervention_surface` and `measurement_protocol` share no files, that the loop can only edit the surface, and that `held_out_confirmation` is reserved and never referenced by the search. Reject if they overlap — an overlap lets the loop tune its own metric (goalpost-moving).
```

**Step 2: Verify the edit landed**

Run:
```bash
grep -n "disjoint and frozen" agents/preregistration-reviewer.md; echo "exit=$?"
```
Expected: one matching line, `exit=0`.

**Step 3: Commit**

Run:
```bash
git add agents/preregistration-reviewer.md
git commit -m "feat: preregistration-reviewer checks frozen-apparatus disjointness

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

### Task 15: Phase 1 acceptance — full harness green

**Step 1: Run the entire deterministic harness**

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
------------------------------------------
ALL EXPERIMENT-LOOP HELPER TESTS PASSED (6 files)
exit=0
```

**Step 2: Confirm all helpers are executable**

Run:
```bash
ls -l scripts/experiment-loop/*.sh | awk '{print $1, $NF}'
```
Expected: each `.sh` shows `-rwxr-xr-x` (executable).

**Step 3: Final Phase 1 commit (no-op safety commit if anything was left unstaged)**

Run:
```bash
git status --porcelain
```
Expected: empty output (everything already committed). If not empty, stage and commit the remainder with message `chore: finalize phase 1 experiment-loop mechanics`.

---

## Phase 1 Done — Definition of Done

- [ ] `bash scripts/experiment-loop/tests/run_all.sh` exits `0` with 6 passing test files.
- [ ] `scripts/experiment-loop/{freeze_gate,decide,ledger_append,promote}.sh` exist and are executable.
- [ ] `templates/experiment-ledger.yaml` parses as valid YAML.
- [ ] `templates/preregistration.yaml` contains the `experiment_loop` frozen-apparatus block (all 13 fields present per the Task 12 test).
- [ ] `agents/preregistration-reviewer.md` has the disjointness checklist item.
- [ ] Every task committed locally; nothing pushed.

**Next:** Phase 2 builds the loop recipe + `experiment-runner` agent + `/execute` dispatch + bundle registration on top of these helpers and schemas.
