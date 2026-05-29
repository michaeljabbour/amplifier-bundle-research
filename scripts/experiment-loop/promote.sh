#!/usr/bin/env bash
set -uo pipefail

ledger="${1:?usage: promote.sh <ledger_file> <confirmation_block_file> [commit_msg]}"
block="${2:?missing <confirmation_block_file>}"
msg="${3:-ledger: append confirmation block}"

if [ ! -f "$ledger" ]; then
    echo "promote: ledger file not found: $ledger" >&2
    exit 2
fi

if [ ! -f "$block" ]; then
    echo "promote: block file not found: $block" >&2
    exit 2
fi

if ! grep -q 'confirmation:' "$block"; then
    echo "promote: block missing 'confirmation:' key — refusing" >&2
    exit 3
fi

cat "$block" >> "$ledger"
git add "$ledger"
git commit -m "$msg" -- "$ledger" >/dev/null
echo "promote: appended confirmation block to $ledger"
exit 0
