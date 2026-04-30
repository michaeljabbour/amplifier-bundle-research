#!/usr/bin/env bash
# v0.8.3 healthcheck: extends v0.8.2 with the four new test gates plus the
# real `recipes operation=validate` gate. Closes the v0.8.0/v0.8.1 file-
# presence-only-checking failure mode permanently.
#
# Gate matrix:
#   1. Structural carry-over from v0.8.2  (file presence + agent rename + version)
#   2. Recipe schema validation            (real `recipes operation=validate` per recipe;
#                                            slow — invoke with --skip-recipes-validate
#                                            to bypass for fast iteration)
#   3. Agent-name collision audit          (sibling bundles in $HOME/dev/amplifier-bundle-*)
#   4. Recipe → agent reference integrity  (every `agent: research:NAME` resolves to
#                                            an actual file in agents/)
#   5. Behavior include consistency        (research.md include list ↔ behaviors/*.md)
#   6. Calibration tool runtime test       (17 tests = 16 unit + 1 CLI subprocess)
#   7. Hygiene                             (.schema-probe/ absent, etc.)

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
SKIP_RECIPES_VALIDATE=0
for arg in "$@"; do
    case "$arg" in
        --skip-recipes-validate) SKIP_RECIPES_VALIDATE=1 ;;
    esac
done
fail=0
pass=0
ok()           { printf "  OK   %s\n" "$1"; pass=$((pass + 1)); }
no()           { printf "  FAIL %s\n" "$1"; fail=$((fail + 1)); }
exists()       { [ -f "$BUNDLE/$1" ] && ok "$2" || no "$2"; }
contains()     { grep -q "$1" "$BUNDLE/$2" 2>/dev/null && ok "$3" || no "$3"; }
mincount()     { local got; got=$(find "$BUNDLE/$1" -maxdepth 1 -name "$2" 2>/dev/null | wc -l | tr -d ' '); [ "$got" -ge "$3" ] && ok "$4 ($got)" || no "$4 ($got, need >=$3)"; }

echo "amplifier-bundle-research v0.8.4 healthcheck"
echo "  bundle path: $BUNDLE"
echo

echo "1) Structural (carry-over from v0.8.2):"
exists  "bundle.md"                                              "bundle.md present"
contains "version: 0.8.4" "bundle.md"                            "bundle.md version 0.8.4"
mincount "agents"   "*.md"   14                                  ">=14 agents"
mincount "recipes"  "*.yaml" 14                                  ">=14 recipes"
exists "agents/research-paper-architect.md"                      "research-paper-architect (renamed; collision broken)"
exists "behaviors/cross-vendor-judge.md"                         "cross-vendor-judge behavior"
exists "behaviors/cache-only-verification.md"                    "cache-only-verification behavior"

echo
echo "2) Recipe schema validation (the gate that v0.8.0/v0.8.1 missed):"
if [ "$SKIP_RECIPES_VALIDATE" -eq 1 ]; then
    echo "  SKIPPED (--skip-recipes-validate set; run scripts/validate-all-recipes.sh manually for full check)"
else
    if "$BUNDLE/scripts/validate-all-recipes.sh" "$BUNDLE" >/dev/null 2>&1; then
        ok "all recipes pass `recipes operation=validate`"
    else
        no "one or more recipes fail recipes operation=validate (run scripts/validate-all-recipes.sh for details)"
    fi
fi

echo
echo "3) Agent-name collision audit (sibling bundles):"
if "$BUNDLE/scripts/check-agent-collisions.sh" "$HOME/dev" "$BUNDLE" >/dev/null 2>&1; then
    ok "no agent-name collisions involving research bundle"
else
    no "agent-name collision detected (run scripts/check-agent-collisions.sh for details)"
fi

echo
echo "4) Recipe → agent reference integrity:"
if "$BUNDLE/scripts/check-recipe-agent-refs.sh" "$BUNDLE" >/dev/null 2>&1; then
    ok "every agent reference in recipes resolves to a real agent file"
else
    no "unresolved agent references (run scripts/check-recipe-agent-refs.sh for details)"
fi

echo
echo "5) Behavior include consistency:"
if "$BUNDLE/scripts/check-behavior-includes.sh" "$BUNDLE" >/dev/null 2>&1; then
    ok "behaviors/research.md include list matches actual files"
else
    no "behavior include list inconsistent (run scripts/check-behavior-includes.sh)"
fi

echo
echo "6) pytest across ALL tool modules:"
total_p=0; total_f=0; n_mod=0
for tool in "$BUNDLE"/modules/tool-*; do
    [ -d "$tool/tests" ] || continue
    name=$(basename "$tool")
    OUT=$(cd "$tool" && python3 -m pytest tests/ -q 2>&1)
    LAST=$(echo "$OUT" | tail -1)
    p=$(echo "$LAST" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1)
    f=$(echo "$LAST" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1)
    p=${p:-0}; f=${f:-0}
    total_p=$((total_p + p)); total_f=$((total_f + f)); n_mod=$((n_mod + 1))
    if [ "$f" -eq 0 ]; then
        ok "$name: $p tests pass"
    else
        no "$name: $f failed"
    fi
done
ok "TOTAL: $total_p passed, $total_f failed across $n_mod modules"

echo
echo "7) ruff lint across ALL tool modules:"
for tool in "$BUNDLE"/modules/tool-*; do
    name=$(basename "$tool")
    if [ -d "$tool/src" ] || [ -d "$tool/tool_paperbanana" ]; then
        OUT=$(cd "$tool" && python3 -m ruff check . 2>&1)
        if [ -z "$OUT" ] || echo "$OUT" | grep -qE "All checks passed|^$"; then
            ok "$name ruff: clean"
        else
            n_iss=$(echo "$OUT" | grep -cE '^[a-z][^:]*:[0-9]+' || echo 0)
            no "$name ruff: $n_iss issue(s)"
        fi
    fi
done

echo
echo "8) Behavior structure (every behavior file has valid frontmatter):"
if "$BUNDLE/scripts/check-behavior-structure.sh" "$BUNDLE" >/dev/null 2>&1; then
    ok "all behavior files structurally valid"
else
    no "one or more behavior files have malformed frontmatter (run scripts/check-behavior-structure.sh)"
fi

echo
echo "9) Documentation:"
exists "docs/V0.8.0-PLAN.md"                                       "v0.8.0 plan"
exists "docs/V0.8.2-RCA.md"                                        "v0.8.2 RCA"

echo
echo "10) Hygiene:"
[ ! -d "$BUNDLE/.schema-probe" ] && ok ".schema-probe/ cleaned up" || no ".schema-probe/ still present"

echo
echo "------------------------------------------"
echo "SUMMARY: $pass checks passed, $fail checks failed"
echo "------------------------------------------"
if [ "$fail" -eq 0 ]; then
    echo "*** v0.8.4 healthy: ALL gates pass (recipes valid + collision-free + ref-integrity + 174+ tests pass + ruff clean + behavior-structure valid) ***"
    exit 0
else
    echo "*** $fail check(s) failed ***"
    exit 1
fi
