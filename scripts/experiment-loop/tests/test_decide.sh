#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DECIDE="$HERE/../decide.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t
git config user.name t
echo "base" > f.txt; git add -A; git commit -qm "baseline"
BASE=$(git rev-parse HEAD)
echo "intervention" >> f.txt; git add -A; git commit -qm "intervention"

# Test keep: intervention commit must survive
bash "$DECIDE" keep >/dev/null
if [ "$(git rev-parse HEAD)" = "$BASE" ]; then
    echo "FAIL: keep dropped the commit"
    exit 1
fi

# Test revert: HEAD must return to baseline with a clean tree
bash "$DECIDE" revert >/dev/null
if [ "$(git rev-parse HEAD)" != "$BASE" ]; then
    echo "FAIL: revert did not reset to baseline"
    exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
    echo "FAIL: revert left a dirty tree"
    exit 1
fi

# Test invalid: must exit 2
bash "$DECIDE" bogus >/dev/null 2>&1
if [ "$?" -ne 2 ]; then
    echo "FAIL: invalid decision did not exit 2"
    exit 1
fi

echo "PASS: decide"
exit 0
