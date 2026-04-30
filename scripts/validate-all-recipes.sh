#!/usr/bin/env bash
# Validate every recipe in this bundle against the recipe-engine's schema.
# Runs `amplifier tool invoke recipes operation=validate recipe_path=<path>`
# on each *.yaml file in recipes/. Fails on any INVALID.
#
# This is the gate that v0.8.0/v0.8.1 missed — file presence is not enough;
# the recipes have to actually parse against the engine schema.

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0

cd "$BUNDLE" || { echo "FATAL: bundle path not found: $BUNDLE"; exit 1; }

if [ ! -d "recipes" ]; then
    echo "FATAL: no recipes/ directory at $BUNDLE"
    exit 1
fi

echo "Validating all recipes in $BUNDLE/recipes/..."
echo

# Iterate all .yaml files at the top level of recipes/
for recipe in recipes/*.yaml; do
    [ -f "$recipe" ] || continue
    # Skip internal smoke-test recipes (prefix with underscore)
    base=$(basename "$recipe")
    case "$base" in
        _*) continue ;;
    esac
    OUT=$(amplifier tool invoke recipes operation=validate recipe_path="$recipe" 2>&1)
    EX=$?
    if [ $EX -eq 0 ] && echo "$OUT" | grep -qE '"status": "valid"|valid'; then
        printf "  OK   %s\n" "$recipe"
        pass=$((pass + 1))
    else
        printf "  FAIL %s\n" "$recipe"
        echo "$OUT" | tail -3 | sed 's/^/         /'
        fail=$((fail + 1))
    fi
done

echo
echo "------------------------------------------"
echo "RECIPE VALIDATION: $pass valid, $fail invalid"
echo "------------------------------------------"
[ "$fail" -eq 0 ] && exit 0 || exit 1
