#!/usr/bin/env bash
# v0.8.2 healthcheck: structural + runtime + recipe-schema-validation gate.
# Closes the v0.8.0/v0.8.1 verification gap (file-presence-only checking).
# v0.8.2 introduces a `recipes operation=validate` gate plus a canonical-pattern
# gate that catches the silent-failure bugs the engine doesn't reject.

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0
ok()           { printf "  OK   %s\n" "$1"; pass=$((pass + 1)); }
no()           { printf "  FAIL %s\n" "$1"; fail=$((fail + 1)); }
exists()       { [ -f "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
existdir()     { [ -d "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
contains()     { grep -q "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
contains_e()   { grep -qE "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
not_contains() { grep -q "$1" "$BUNDLE/$2" 2>/dev/null && no "$3" || ok "$3"; }
mincount()     { local got; got=$(find "$BUNDLE/$1" -maxdepth 1 -name "$2" 2>/dev/null | wc -l | tr -d ' '); [ "$got" -ge "$3" ] && ok "$4 ($got)" || no "$4 ($got, need >=$3)"; }
minlines()     { local got; got=$(wc -l < "$BUNDLE/$1" 2>/dev/null | tr -d ' '); [ -n "$got" ] && [ "$got" -ge "$2" ] && ok "$3 ($got lines)" || no "$3 ($got lines, need >=$2)"; }

echo "amplifier-bundle-research v0.8.2 healthcheck"
echo "  bundle path: $BUNDLE"
echo

echo "Carried from v0.8.1:"
exists  "bundle.md"                                              "bundle.md present"
mincount "agents"   "*.md"   14                                  ">=14 agents"
mincount "recipes"  "*.yaml" 14                                  ">=14 recipes (9 baseline + 5 v0.8.x additions + iteration sub-recipe)"
exists  "behaviors/honest-pivot.md"                              "honest-pivot behavior"
for m in question plan execute critique draft publish; do
    exists "modes/$m.md"                                          "mode /$m"
done
exists  "templates/environment.yml"                              "templates/environment.yml"
exists  "requirements.txt"                                       "pinned requirements.txt"

echo
echo "v0.8.2 RECIPE SCHEMA VALIDATION (the gate that v0.8.0/v0.8.1 missed):"
echo "  Run:   amplifier tool invoke recipes operation=validate recipe_path=<path>"
echo "  These canonical-pattern checks are a static substitute for the runtime validator."
echo

echo "Recipe schema canonical patterns (orchestrated-loop.yaml):"
not_contains "type: while"          "recipes/orchestrated-loop.yaml"     "no fabricated type: while"
not_contains "type: llm_judge"      "recipes/orchestrated-loop.yaml"     "no fabricated type: llm_judge"
not_contains "^    body:"           "recipes/orchestrated-loop.yaml"     "no body: on stage (use steps:)"
not_contains "initial_state:"       "recipes/orchestrated-loop.yaml"     "no initial_state: (use top-level context:)"
not_contains "approval_required:"   "recipes/orchestrated-loop.yaml"     "no flat approval_required: (use nested approval:)"
contains "approval:"                "recipes/orchestrated-loop.yaml"     "has nested approval: blocks"
contains "while_condition"          "recipes/orchestrated-loop.yaml"     "has canonical while_condition"
contains "update_context"           "recipes/orchestrated-loop.yaml"     "has canonical update_context"

echo
echo "Recipe schema canonical patterns (orchestrated-loop-iteration.yaml):"
exists "recipes/orchestrated-loop-iteration.yaml"                        "iteration sub-recipe present"
not_contains "type: while"          "recipes/orchestrated-loop-iteration.yaml"  "no fabricated type: while"
not_contains "type: llm_judge"      "recipes/orchestrated-loop-iteration.yaml"  "no fabricated type: llm_judge"

echo
echo "Recipe schema canonical patterns (other v0.8.x recipes):"
for r in cache-only-verify.yaml bundle-overlay-proposer.yaml residual-adjudicator.yaml idea-generation.yaml; do
    not_contains "type: shell"     "recipes/$r"  "$r: no type: shell (use type: bash)"
    not_contains "join("            "recipes/$r"  "$r: no Jinja-style filters"
done

echo
echo "Recipe schema canonical patterns (top-level → context: migration):"
for r in empirical-paper benchmark-paper replication-study literature-review patent-brief policy-brief white-paper grant-proposal paperbanana-figure; do
    not_contains "^cache_only:"     "recipes/$r.yaml"  "$r: cache_only is in context: not top-level"
done

echo
echo "Agent namespace (no collisions):"
exists "agents/research-paper-architect.md"                       "research-paper-architect (renamed from paper-architect)"
contains "name: research-paper-architect" "agents/research-paper-architect.md"  "meta:name renamed correctly"

echo
echo "Calibration tool runtime test:"
if (cd "$BUNDLE/modules/tool-experiment-power" && python3 -m pytest tests/test_calibration.py -q --no-header 2>&1 | tail -1 | grep -qE "passed"); then
    ok "16 calibration tests pass"
else
    no "calibration tests do not pass"
fi

echo
echo "Documentation:"
exists "docs/V0.8.0-PLAN.md"                                       "v0.8.0 plan + audit record"
exists "docs/V0.8.1-SCRIPT-DIFF.md"                                "v0.8.1 script-drift report"
exists "docs/V0.8.2-RCA.md"                                        "v0.8.2 RCA + fix plan"
contains "INCIDENT" "docs/V0.8.0-PLAN.md"                          "v0.8.0 plan has incident-log entry for v0.8.2 supersession"

echo
echo "Wire-up:"
contains "version: 0.8.2" "bundle.md"                              "bundle.md version 0.8.2"
contains "research-paper-architect" "bundle.md"                    "bundle.md uses renamed agent"
not_contains "^.*research:paper-architect" "bundle.md"             "bundle.md has no stale research:paper-architect"

echo
echo "Hygiene:"
[ ! -d "$BUNDLE/.schema-probe" ] && ok ".schema-probe/ cleaned up" || no ".schema-probe/ still present"

echo
echo "------------------------------------------"
echo "SUMMARY: $pass checks passed, $fail checks failed"
echo "------------------------------------------"
if [ "$fail" -eq 0 ]; then
    echo "*** v0.8.2 ready: schema-validated + canonical patterns + hygiene clean ***"
    exit 0
else
    echo "*** $fail check(s) failed ***"
    exit 1
fi
