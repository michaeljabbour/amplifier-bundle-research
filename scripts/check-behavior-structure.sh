#!/usr/bin/env bash
# Verify every behavior file in behaviors/ is structurally valid:
#  1. Begins with `---` (YAML frontmatter open)
#  2. Has a `bundle:` block with `name:` field
#  3. Closes the frontmatter with a second `---`
#
# Note: behaviors are configuration files. The markdown body is documentation
# and can be very short (cross-vendor-judge has 7 lines of body and is fine).
# We do NOT enforce a minimum body length.

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
fail=0
pass=0

for behavior in "$BUNDLE"/behaviors/*.md; do
    [ -f "$behavior" ] || continue
    name=$(basename "$behavior" .md)

    # Check 1: starts with ---
    if ! head -1 "$behavior" | grep -qE '^---$'; then
        printf "  FAIL %s: does not start with frontmatter ---\n" "$name"
        fail=$((fail + 1))
        continue
    fi

    # Check 2: has bundle: block with name:
    fm=$(awk '/^---$/{c++; if (c==2) exit} c==1 {print}' "$behavior")
    if ! echo "$fm" | grep -qE '^bundle:'; then
        printf "  FAIL %s: missing bundle: block in frontmatter\n" "$name"
        fail=$((fail + 1))
        continue
    fi
    if ! echo "$fm" | grep -qE '^  name:'; then
        printf "  FAIL %s: missing bundle.name field\n" "$name"
        fail=$((fail + 1))
        continue
    fi

    # Check 3: closing --- present
    n_dashes=$(grep -cE '^---$' "$behavior")
    if [ "$n_dashes" -lt 2 ]; then
        printf "  FAIL %s: frontmatter not closed (only %s --- markers)\n" "$name" "$n_dashes"
        fail=$((fail + 1))
        continue
    fi

    name_val=$(echo "$fm" | grep -E '^  name:' | head -1 | sed 's/.*name:[[:space:]]*//')
    printf "  OK   %s (bundle.name=%s)\n" "$name" "$name_val"
    pass=$((pass + 1))
done

echo
echo "------------------------------------------"
echo "BEHAVIOR STRUCTURE: $pass valid, $fail invalid"
echo "------------------------------------------"
[ $fail -eq 0 ] && exit 0 || exit 1
