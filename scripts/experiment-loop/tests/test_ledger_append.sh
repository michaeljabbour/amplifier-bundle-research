#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPEND="$HERE/../ledger_append.sh"
DECIDE="$HERE/../decide.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t
git config user.name t
mkdir -p experiments src
echo "base" > src/train.py; git add -A; git commit -qm "baseline"
LEDGER="experiments/ledger.yaml"

# Row 1
printf -- '- iteration: 1\n  decision: keep\n' > row1.txt
bash "$APPEND" "$LEDGER" row1.txt "ledger: iter 1" >/dev/null
if ! test -f "$LEDGER"; then
    echo "FAIL: ledger not created"
    exit 1
fi
if ! grep -q "iteration: 1" "$LEDGER"; then
    echo "FAIL: row1 missing"
    exit 1
fi

# Reverted intervention
echo "tweak" >> src/train.py; git add -A; git commit -qm "intervention"
printf -- '- iteration: 2\n  decision: revert\n' > row2.txt
bash "$DECIDE" revert >/dev/null
bash "$APPEND" "$LEDGER" row2.txt "ledger: iter 2" >/dev/null

# Assert both rows survive
if ! grep -q "iteration: 1" "$LEDGER"; then
    echo "FAIL: revert deleted row1"
    exit 1
fi
if ! grep -q "iteration: 2" "$LEDGER"; then
    echo "FAIL: row2 missing"
    exit 1
fi

# Assert the ledger commit is its own separate commit
SUBJECT=$(git log -1 --pretty=%s)
case "$SUBJECT" in
    ledger:*) : ;;
    *) echo "FAIL: last commit is not a separate ledger commit ($SUBJECT)"; exit 1 ;;
esac

echo "PASS: ledger_append"
exit 0
