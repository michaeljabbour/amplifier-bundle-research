#!/usr/bin/env bash
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/.."

FREEZE="$SCRIPTS/freeze_gate.sh"
DECIDE="$SCRIPTS/decide.sh"
APPEND="$SCRIPTS/ledger_append.sh"
PROMOTE="$SCRIPTS/promote.sh"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cd "$TMP"
git init -q
git config user.email t@t
git config user.name t

mkdir -p surface experiments
echo frozen > eval.txt
echo base > surface/train.txt
git add -A
git commit -qm "baseline"

printf 'surface/*\n' > allow.txt
LEDGER=experiments/ledger.yaml

# ---- iteration 1: KEEP ----
echo iter1 >> surface/train.txt
git add -- surface/train.txt
git commit -qm "intervention 1"

if ! bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
    echo "FAIL: iter1 freeze_gate rejected an in-surface change"
    exit 1
fi

cat > r1.txt <<'EOF'
- iteration: 1
  decision: keep
  label: exploratory
EOF

bash "$DECIDE" keep >/dev/null
bash "$APPEND" "$LEDGER" r1.txt >/dev/null

# ---- iteration 2: REVERT ----
echo iter2 >> surface/train.txt
git add -- surface/train.txt
git commit -qm "intervention 2"

if ! bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
    echo "FAIL: iter2 freeze_gate rejected an in-surface change"
    exit 1
fi

cat > r2.txt <<'EOF'
- iteration: 2
  decision: revert
  label: exploratory
EOF

bash "$DECIDE" revert >/dev/null
bash "$APPEND" "$LEDGER" r2.txt >/dev/null

# ---- iteration 3: KEEP ----
echo iter3 >> surface/train.txt
git add -- surface/train.txt
git commit -qm "intervention 3"

if ! bash "$FREEZE" allow.txt "HEAD~1 HEAD" >/dev/null 2>&1; then
    echo "FAIL: iter3 freeze_gate rejected an in-surface change"
    exit 1
fi

cat > r3.txt <<'EOF'
- iteration: 3
  decision: keep
  label: exploratory
EOF

bash "$DECIDE" keep >/dev/null
bash "$APPEND" "$LEDGER" r3.txt >/dev/null

# ---- promotion gate ----
cat > conf.txt <<'EOF'
- confirmation:
    confirms_iteration: 3
    label: confirmatory
    meta_verdict: promote
EOF

bash "$PROMOTE" "$LEDGER" conf.txt >/dev/null

# ---- assertions ----
ROWS=$(grep -c '^- iteration:' "$LEDGER")
if [ "$ROWS" -ne 3 ]; then
    echo "FAIL: expected 3 ledger rows, got $ROWS"
    exit 1
fi

KEEPS=$(grep -c 'decision: keep' "$LEDGER")
REVERTS=$(grep -c 'decision: revert' "$LEDGER")

if [ "$KEEPS" -lt 1 ] || [ "$REVERTS" -lt 1 ]; then
    echo "FAIL: expected >=1 keeps and >=1 reverts (keeps=$KEEPS reverts=$REVERTS)"
    exit 1
fi

for n in 1 2 3; do
    if ! grep -q "^- iteration: $n$" "$LEDGER"; then
        echo "FAIL: revert deleted ledger row for iteration $n"
        exit 1
    fi
done

if ! grep -q 'confirms_iteration: 3' "$LEDGER"; then
    echo "FAIL: confirmation block not appended"
    exit 1
fi

echo "PASS: smoke_end_to_end (3 rows; keeps=$KEEPS reverts=$REVERTS; confirmation appended)"
exit 0
