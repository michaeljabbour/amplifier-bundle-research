#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/../freeze_gate.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t
git config user.name t
mkdir -p src
echo "base" > src/train.py
echo "frozen" > eval.py
git add -A; git commit -qm "baseline"
printf 'src/*\n' > allow.txt
# Case 1 (in-surface): change inside src/ must be allowed
echo "# change" >> src/train.py
git add -A; git commit -qm "in-surface change"
if ! bash "$GATE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
    echo "FAIL: in-surface change was rejected"
    exit 1
fi
# Case 2 (out-of-surface): change outside src/ must be rejected
echo "# change" >> eval.py
git add -A; git commit -qm "out-of-surface change"
if bash "$GATE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
    echo "FAIL: out-of-surface change was allowed"
    exit 1
fi
echo "PASS: freeze_gate"
exit 0
