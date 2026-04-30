#!/usr/bin/env bash
# For every `agent: research:NAME` reference in recipes/, verify NAME exists as
# a real agent file. Catches typos and stale references after agent renames.

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0

cd "$BUNDLE" || { echo "FATAL: bundle path not found: $BUNDLE"; exit 1; }

# Build the set of valid agent names (by their meta:name field)
VALID_NAMES=$(mktemp)
trap 'rm -f "$VALID_NAMES"' EXIT

for f in agents/*.md; do
    [ -f "$f" ] || continue
    name=$(awk '/^  *name:/ {sub(/^  *name:[[:space:]]*/, ""); print; exit}' "$f")
    [ -n "$name" ] && echo "$name" >> "$VALID_NAMES"
done

# Scan every recipe for `agent: research:<name>` references
echo "Agent reference audit (recipes → agents/<name>.md):"
echo
for recipe in recipes/*.yaml; do
    [ -f "$recipe" ] || continue
    # Find all references like "agent: research:foo" or "agent: research:foo-bar"
    while IFS= read -r ref; do
        name="${ref#research:}"
        if grep -qFx "$name" "$VALID_NAMES"; then
            pass=$((pass + 1))
        else
            printf "  FAIL: %s references undefined agent: research:%s\n" "$recipe" "$name"
            fail=$((fail + 1))
        fi
    done < <(grep -oE 'agent:[[:space:]]+research:[a-z-]+' "$recipe" | awk '{print $2}' | sort -u)
done

echo
echo "------------------------------------------"
echo "AGENT REFERENCE AUDIT: $pass valid, $fail unresolved"
echo "------------------------------------------"
[ "$fail" -eq 0 ] && exit 0 || exit 1
