#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DOC="$REPO_ROOT/context/autonomous-loop-awareness.md"

fail() { echo "FAIL: $1"; exit 1; }

# 1. File exists
[ -f "$DOC" ] || fail "autonomous-loop-awareness.md missing"

# 2. Key phrases present
for phrase in 'When to reach for the loop' 'Honest limits' 'greedy search' 'confirmatory' 'intervention_surface'; do
    grep -qi "$phrase" "$DOC" || fail "missing phrase: $phrase"
done

echo "PASS: awareness_context"
exit 0
