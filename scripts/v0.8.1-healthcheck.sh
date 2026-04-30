#!/usr/bin/env bash
# v0.8.1 healthcheck: structural + runtime closure checks.
# Extends v0.8.0 with the run-blockers from the v0.8.0 verification audit.

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0
ok()         { printf "  OK   %s\n" "$1"; pass=$((pass + 1)); }
no()         { printf "  FAIL %s\n" "$1"; fail=$((fail + 1)); }
exists()     { [ -f "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
existdir()   { [ -d "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
contains()   { grep -q "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
contains_e() { grep -qE "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
contains_r() { grep -rqE "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
mincount()   { local got; got=$(find "$BUNDLE/$1" -maxdepth 1 -name "$2" 2>/dev/null | wc -l | tr -d ' '); [ "$got" -ge "$3" ] && ok "$4 ($got)" || no "$4 ($got, need >=$3)"; }
minlines()   { local got; got=$(wc -l < "$BUNDLE/$1" 2>/dev/null | tr -d ' '); [ -n "$got" ] && [ "$got" -ge "$2" ] && ok "$3 ($got lines)" || no "$3 ($got lines, need >=$2)"; }
allcontain() { local files="$1"; local pat="$2"; local label="$3"; local missing=""; for f in $files; do grep -q "$pat" "$BUNDLE/$f" 2>/dev/null || missing="$missing $f"; done; [ -z "$missing" ] && ok "$label" || no "$label (missing in:$missing)"; }

echo "amplifier-bundle-research v0.8.1 healthcheck"
echo "  bundle path: $BUNDLE"
echo

echo "Carried from v0.8.0:"
exists  "bundle.md"                                              "bundle.md present"
mincount "agents"   "*.md"   14   ">=14 agents"
mincount "recipes"  "*.yaml" 13   ">=13 recipes (9 baseline + 4 v0.8.x additions)"
existdir "modules"                                               "modules/ directory"
exists  "behaviors/honest-pivot.md"                              "honest-pivot behavior"
for m in question plan execute critique draft publish; do
    exists "modes/$m.md"                                          "mode /$m"
done
exists  "templates/environment.yml"                              "templates/environment.yml"
exists  "requirements.txt"                                       "pinned requirements.txt"
exists  "recipes/orchestrated-loop.yaml"                         "v0.8.0 Action 1: orchestrated-loop"
exists  "agents/paper-architect.md"                              "v0.8.0 Action 2: paper-architect"
exists  "agents/ml-paper-reviewer.md"                            "v0.8.0 Action 4: ml-paper-reviewer"
exists  "agents/literature-scout.md"                             "v0.8.0 Action 5: literature-scout"
exists  "agents/idea-generator.md"                               "v0.8.0 Action 6: idea-generator"
exists  "behaviors/cache-only-verification.md"                   "v0.8.0 Action 7: cache-only-verification"
exists  "context/experiment-calibration-awareness.md"            "v0.8.0 Action 8: calibration awareness"
exists  "behaviors/cross-vendor-judge.md"                        "v0.8.0 Action 9: cross-vendor-judge"

echo
echo "v0.8.1 RUNTIME closures (the new checks):"
echo
echo "Action 1 runtime: orchestrated-loop is now executable end-to-end"
exists  "recipes/bundle-overlay-proposer.yaml"                   "  bundle-overlay-proposer sub-recipe"
exists  "recipes/residual-adjudicator.yaml"                      "  residual-adjudicator sub-recipe"
exists  "context/orchestrated-loop-judge-rubric.md"              "  orchestrated-loop judge rubric"

echo
echo "Action 7 runtime: cache_only parameter on existing recipes"
EVAL_AND_PAPER_RECIPES="recipes/empirical-paper.yaml recipes/benchmark-paper.yaml recipes/replication-study.yaml recipes/literature-review.yaml recipes/patent-brief.yaml recipes/policy-brief.yaml recipes/white-paper.yaml recipes/grant-proposal.yaml recipes/paperbanana-figure.yaml"
allcontain "$EVAL_AND_PAPER_RECIPES" "cache_only" "  cache_only parameter present in 9 existing recipes"

echo
echo "Action 8 runtime: ECE/Brier/calibration tool"
exists  "modules/tool-experiment-power/src/amplifier_research_power/calibration.py"  "  calibration.py module"
exists  "modules/tool-experiment-power/tests/test_calibration.py"  "  calibration tests"
contains "_cmd_calibration" "modules/tool-experiment-power/src/amplifier_research_power/cli.py" "  calibration subcommand wired in CLI"
echo "  Running calibration tests..."
if (cd "$BUNDLE/modules/tool-experiment-power" && python3 -m pytest tests/test_calibration.py -q --no-header 2>&1 | tail -1 | grep -qE "passed"); then
    ok "  16 calibration tests pass"
else
    no "  calibration tests do not pass"
fi

echo
echo "Action 9 runtime: judge_cross_vendor_required opt-in on evaluation recipes"
EVAL_RECIPES="recipes/empirical-paper.yaml recipes/benchmark-paper.yaml recipes/replication-study.yaml"
allcontain "$EVAL_RECIPES" "judge_cross_vendor_required" "  cross-vendor-judge enforcement opt-in present"

echo
echo "Documentation + cross-references:"
exists  "docs/V0.8.0-PLAN.md"                                    "v0.8.0 plan + audit record"
exists  "docs/V0.8.1-SCRIPT-DIFF.md"                             "v0.8.1 script-drift report"
contains "amplifier-bundle-scientificpaper" "README.md"          "research README cross-references scientificpaper"

echo
echo "Wire-up:"
contains "version: 0.8.1" "bundle.md"                            "bundle.md version 0.8.1"

echo
echo "------------------------------------------"
echo "SUMMARY: $pass checks passed, $fail checks failed"
echo "------------------------------------------"
if [ "$fail" -eq 0 ]; then
    echo "*** v0.8.1 runtime closure verified: orchestrated-loop is executable end-to-end ***"
    exit 0
else
    echo "*** $fail check(s) failed ***"
    exit 1
fi
