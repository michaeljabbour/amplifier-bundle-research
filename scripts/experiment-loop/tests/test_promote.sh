#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMOTE="$HERE/../promote.sh"
APPEND="$HERE/../ledger_append.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
git init -q
git config user.email t@t
git config user.name t
mkdir -p experiments
echo "base" > f.txt; git add -A; git commit -qm "baseline"
LEDGER="experiments/ledger.yaml"

# Seed a row with label: exploratory
printf -- '- iteration: 7\n  decision: keep\n  label: exploratory\n' > row.txt
bash "$APPEND" "$LEDGER" row.txt "ledger: iter 7" >/dev/null

# Valid confirmation block
cat > conf.txt <<'EOF'
- confirmation:
    confirms_iteration: 7
    label: confirmatory
    meta_verdict: promote
EOF

bash "$PROMOTE" "$LEDGER" conf.txt "ledger: confirm iter 7" >/dev/null

if ! grep -q "confirms_iteration: 7" "$LEDGER"; then
    echo "FAIL: confirmation not appended"
    exit 1
fi

if ! grep -q "label: exploratory" "$LEDGER"; then
    echo "FAIL: original row was mutated"
    exit 1
fi

# Invalid block (missing confirmation: key) must exit 3
printf 'garbage: true\n' > bad.txt
bash "$PROMOTE" "$LEDGER" bad.txt >/dev/null 2>&1
if [ "$?" -ne 3 ]; then
    echo "FAIL: bad block not refused with exit 3"
    exit 1
fi

echo "PASS: promote"
exit 0
