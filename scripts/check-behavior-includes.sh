#!/usr/bin/env bash
# Verify behaviors/research.md (composite include list) is consistent with
# the actual files in behaviors/.
#   1. Every `- bundle: research:behaviors/X.md` reference must point to a
#      real file in behaviors/X.md.
#   2. Every behavior file in behaviors/ should be listed in research.md
#      (or be deliberately excluded — we'll allow the composite itself).

set -uo pipefail
BUNDLE="${1:-$HOME/dev/amplifier-bundle-research}"
COMPOSITE="$BUNDLE/behaviors/research.md"
fail=0
pass=0

if [ ! -f "$COMPOSITE" ]; then
    echo "FATAL: composite missing: $COMPOSITE"
    exit 1
fi

# Extract include list from research.md frontmatter
INCLUDED=$(grep -E '^\s*- bundle: research:behaviors/' "$COMPOSITE" \
           | sed 's|.*research:behaviors/||;s|.md.*||' \
           | sort -u)

# Actual files in behaviors/ (excluding research.md itself)
ACTUAL=$(find "$BUNDLE/behaviors" -maxdepth 1 -name '*.md' -not -name 'research.md' \
         | xargs -n1 basename | sed 's/.md$//' | sort -u)

echo "Behavior include audit:"
echo

# Check 1: every included behavior has a real file
echo "  Behaviors listed in research.md but missing as files:"
missing_files=$(comm -23 <(echo "$INCLUDED") <(echo "$ACTUAL"))
if [ -z "$missing_files" ]; then
    printf "    (none)\n"
else
    echo "$missing_files" | sed 's/^/    FAIL /'
    fail=$((fail + $(echo "$missing_files" | wc -l | tr -d ' ')))
fi

# Check 2: every file is in the include list
echo
echo "  Behavior files present but NOT listed in research.md:"
missing_includes=$(comm -13 <(echo "$INCLUDED") <(echo "$ACTUAL"))
if [ -z "$missing_includes" ]; then
    printf "    (none)\n"
else
    echo "$missing_includes" | sed 's/^/    WARN /'  # warning only, not fail
fi

n_included=$(echo "$INCLUDED" | grep -cv '^$')
n_actual=$(echo "$ACTUAL" | grep -cv '^$')
echo
echo "  Included: $n_included; actual files: $n_actual"

[ $fail -eq 0 ] && exit 0 || exit 1
