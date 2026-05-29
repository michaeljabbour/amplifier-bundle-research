#!/usr/bin/env bash
set -uo pipefail

ledger="${1:?usage: ledger_append.sh <ledger_file> <row_file> [commit_msg]}"
row="${2:?missing <row_file>}"
msg="${3:-ledger: append iteration row}"

if [ ! -f "$row" ]; then
    echo "ledger_append: row file not found: $row" >&2
    exit 2
fi

if [ ! -f "$ledger" ]; then
    printf '# experiment ledger (append-only). See templates/experiment-ledger.yaml\n' > "$ledger"
fi

cat "$row" >> "$ledger"
git add "$ledger"
git commit -m "$msg" -- "$ledger" >/dev/null
echo "ledger_append: appended row to $ledger and committed it separately"
exit 0
