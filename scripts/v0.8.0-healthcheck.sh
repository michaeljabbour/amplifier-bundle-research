#!/usr/bin/env bash
# v0.8.0 healthcheck for amplifier-bundle-research
# Verifies the audit-closure capabilities are present and the bundle is structurally healthy.
#
# Usage:  scripts/v0.8.0-healthcheck.sh [BUNDLE_PATH]
# Returns: 0 if all checks pass; non-zero if any check fails (count printed)

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0

ok()   { printf "  OK   %s\n" "$1"; pass=$((pass + 1)); }
no()   { printf "  FAIL %s\n" "$1"; fail=$((fail + 1)); }
exists()    { [ -f "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
existdir()  { [ -d "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
contains()  { grep -q "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
contains_e(){ grep -qE "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
contains_r(){ grep -rqE "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
mincount()  { local got; got=$(find "$BUNDLE/$1" -maxdepth 1 -name "$2" 2>/dev/null | wc -l | tr -d ' '); [ "$got" -ge "$3" ] && ok "$4 ($got found)" || no "$4 ($got found, need >=$3)"; }
minlines()  { local got; got=$(wc -l < "$BUNDLE/$1" 2>/dev/null | tr -d ' '); [ -n "$got" ] && [ "$got" -ge "$2" ] && ok "$3 ($got lines)" || no "$3 ($got lines, need >=$2)"; }

echo "amplifier-bundle-research healthcheck"
echo "  bundle path: $BUNDLE"
echo

echo "Structural (carried from v0.7):"
exists "bundle.md"                                               "bundle.md present"
mincount "agents"   "*.md"   14   ">=14 agents (10 baseline + 4 v0.8 additions)"
mincount "recipes"  "*.yaml" 11   ">=11 recipes (9 baseline + 2 v0.8 additions)"
existdir "modules"                                               "modules/ directory"
exists "behaviors/honest-pivot.md"                               "honest-pivot behavior"
exists "behaviors/exploratory-labeling.md"                       "exploratory-labeling behavior"
for m in question plan execute critique draft publish; do
    exists "modes/$m.md"                                          "mode /$m"
done

echo
echo "Statistical:"
contains_r "McNemar|TOST|Wilson" "context"                       "stats methods documented in context"

echo
echo "Reproducibility:"
exists "templates/environment.yml"                               "templates/environment.yml"
exists "templates/Dockerfile.research"                           "templates/Dockerfile.research"
exists "requirements.txt"                                        "pinned requirements.txt"

echo
echo "v0.8.0 audit-closure additions:"
exists "recipes/orchestrated-loop.yaml"                          "Action 1: orchestrated-loop recipe (H3 enabler)"
exists "agents/paper-architect.md"                               "Action 2: paper-architect agent"
minlines "agents/figure-designer.md"   1500                      "Action 3a: figure-designer surplus merged"
minlines "agents/citation-manager.md"  1000                      "Action 3b: citation-manager surplus merged"
exists "agents/ml-paper-reviewer.md"                             "Action 4: ml-paper-reviewer agent"
contains "calibration warning" "agents/ml-paper-reviewer.md"     "Action 4: calibration warning embedded"
exists "agents/literature-scout.md"                              "Action 5: literature-scout agent"
contains "Semantic Scholar" "agents/literature-scout.md"         "Action 5: Semantic Scholar pattern embedded"
exists "agents/idea-generator.md"                                "Action 6: idea-generator agent"
exists "recipes/idea-generation.yaml"                            "Action 6: idea-generation recipe"
contains_e "Interestingness|interestingness" "agents/idea-generator.md"  "Action 6: 3-axis scoring schema"
exists "behaviors/cache-only-verification.md"                    "Action 7: cache-only-verification behavior"
exists "recipes/cache-only-verify.yaml"                          "Action 7: cache-only-verify recipe"
exists "context/experiment-calibration-awareness.md"             "Action 8: calibration-awareness context"
contains_e "ECE|Brier|reliability diagram" "context/experiment-calibration-awareness.md"  "Action 8: ECE+Brier+reliability covered"
exists "behaviors/cross-vendor-judge.md"                         "Action 9: cross-vendor-judge behavior"
contains "provider_preferences" "behaviors/cross-vendor-judge.md" "Action 9: provider_preferences enforcement"

echo
echo "Wire-up:"
contains "version: 0.8.0" "bundle.md"                            "bundle.md version 0.8.0"
contains "paper-architect" "bundle.md"                           "bundle.md wires paper-architect"
contains "ml-paper-reviewer" "bundle.md"                         "bundle.md wires ml-paper-reviewer"
contains "literature-scout" "bundle.md"                          "bundle.md wires literature-scout"
contains "idea-generator" "bundle.md"                            "bundle.md wires idea-generator"
contains "version: 0.5.0" "behaviors/research.md"                "behaviors/research.md version 0.5.0"
contains "cache-only-verification" "behaviors/research.md"       "research.md wires cache-only-verification"
contains "cross-vendor-judge" "behaviors/research.md"            "research.md wires cross-vendor-judge"

echo
echo "Documentation:"
exists "docs/V0.8.0-PLAN.md"                                     "V0.8.0-PLAN.md durable audit record"
contains "Action 1" "docs/V0.8.0-PLAN.md"                        "V0.8.0-PLAN.md has action checklist"

echo
echo "------------------------------------------"
echo "SUMMARY: $pass checks passed, $fail checks failed"
echo "------------------------------------------"
if [ "$fail" -eq 0 ]; then
    echo "*** Bundle healthy: full PSE/Amplifier-Scientist v0.8.0 capability set enabled ***"
    exit 0
else
    echo "*** $fail check(s) failed ***"
    exit 1
fi
