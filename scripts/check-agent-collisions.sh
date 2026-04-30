#!/usr/bin/env bash
# Scan ~/dev/amplifier-bundle-* for agent meta:name collisions.
# An agent name should be globally unique across installable bundles to avoid
# silent last-mount-wins behavior.

set -uo pipefail
BUNDLE_PARENT="${1:-$HOME/dev}"
SELF_BUNDLE="${2:-$BUNDLE_PARENT/amplifier-bundle-research}"

# Build a list of (bundle, agent_name) pairs across every sibling bundle
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

for bundle_dir in "$BUNDLE_PARENT"/amplifier-bundle-*; do
    [ -d "$bundle_dir/agents" ] || continue
    bundle_name=$(basename "$bundle_dir")
    for f in "$bundle_dir/agents"/*.md; do
        [ -f "$f" ] || continue
        # Extract the meta:name line, accepting any indentation
        name=$(awk '/^  *name:/ {sub(/^  *name:[[:space:]]*/, ""); print; exit}' "$f")
        if [ -n "$name" ]; then
            printf "%s\t%s\n" "$bundle_name" "$name" >> "$TMP"
        fi
    done
done

# Find names that appear in > 1 bundle
echo "Agent name collision audit (across $BUNDLE_PARENT/amplifier-bundle-*):"
echo
fail=0
while IFS= read -r name; do
    bundles=$(awk -F'\t' -v n="$name" '$2 == n {print $1}' "$TMP" | sort -u)
    n_bundles=$(echo "$bundles" | wc -l | tr -d ' ')
    if [ "$n_bundles" -gt 1 ]; then
        echo "  COLLISION: agent '$name' appears in $n_bundles bundles:"
        echo "$bundles" | sed 's/^/    - /'
        # Only flag if SELF_BUNDLE is one of the colliding bundles
        if echo "$bundles" | grep -q "$(basename "$SELF_BUNDLE")"; then
            fail=$((fail + 1))
        fi
    fi
done < <(awk -F'\t' '{print $2}' "$TMP" | sort -u)

echo
[ $fail -eq 0 ] && echo "  No collisions involving $(basename "$SELF_BUNDLE")" || echo "  FAIL: $fail collision(s) involve $(basename "$SELF_BUNDLE")"
exit $fail
