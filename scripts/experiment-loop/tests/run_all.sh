#!/usr/bin/env bash
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

fail=0
ran=0

for t in "$HERE"/test_*.sh; do
  [ -f "$t" ] || continue
  ran=$((ran + 1))
  bash "$t" || {
    echo "  ^ FAILED: $(basename "$t")"
    fail=$((fail + 1))
  }
done

echo "------------------------------------------------------------"
if [ "$ran" -eq 0 ]; then
  echo "NO TESTS FOUND in $HERE"
  exit 1
elif [ "$fail" -eq 0 ]; then
  echo "ALL EXPERIMENT-LOOP HELPER TESTS PASSED ($ran files)"
  exit 0
else
  echo "$fail of $ran TEST FILE(S) FAILED"
  exit 1
fi
