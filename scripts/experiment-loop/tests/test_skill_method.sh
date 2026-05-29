#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILL="$REPO_ROOT/skills/conducting-autonomous-experiments/SKILL.md"

fail() { echo "FAIL: $1"; exit 1; }

# 1. SKILL.md exists
[ -f "$SKILL" ] || fail "SKILL.md missing"

# 2. Frontmatter has ^name: and ^description:
grep -q '^name:' "$SKILL" || fail "frontmatter missing name:"
grep -q '^description:' "$SKILL" || fail "frontmatter missing description:"

# 3. Attribution present
grep -qi 'autoresearch' "$SKILL" || fail "missing autoresearch attribution"
grep -qi 'karpathy' "$SKILL" || fail "missing Karpathy attribution"
grep -q 'MIT' "$SKILL" || fail "missing MIT attribution"

# 4. Judge-panel reference filenames present
grep -q 'cross-vendor-judge.md' "$SKILL" || fail "missing cross-vendor-judge.md reference"
grep -q 'orchestrated-loop-judge-rubric.md' "$SKILL" || fail "missing orchestrated-loop-judge-rubric.md reference"
grep -q 'ml-paper-reviewer.md' "$SKILL" || fail "missing ml-paper-reviewer.md reference"

# 5. Must NOT reference cache-only-verify
grep -q 'cache-only-verify' "$SKILL" && fail "must not reference cache-only-verify"

# 6. Four anti-patterns present
grep -qi 'n=1' "$SKILL" || fail "missing n=1 anti-pattern"
grep -qi 'multiple-comparison' "$SKILL" || fail "missing multiple-comparison anti-pattern"
grep -qi 'no-hypothesis' "$SKILL" || fail "missing no-hypothesis anti-pattern"
grep -qi 'metric monoculture' "$SKILL" || fail "missing metric monoculture anti-pattern"

echo "PASS: skill_method"
exit 0
