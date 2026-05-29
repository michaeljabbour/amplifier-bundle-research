#!/usr/bin/env bash
# freeze_gate.sh — enforce the frozen intervention surface
#
# Purpose: reproduces autoresearch's 'agent may edit train.py, never prepare.py/eval'
# discipline; the intervention_surface allowlist is FROZEN in the hash-locked
# pre-registration and this gate enforces it at commit time.
#
# Usage: freeze_gate.sh <allowlist_file> [diff_spec]
#   allowlist_file  — one shell-glob pattern per line (blank lines and '#' comments ignored)
#   diff_spec       — passed verbatim to `git diff --name-only` (default: HEAD~1 HEAD)
#
# Exit codes:
#   0 — every changed file matches an allowlist pattern
#   1 — one or more files are outside the intervention surface
#   2 — usage/IO error
set -uo pipefail

allowlist="${1:?usage: freeze_gate.sh <allowlist_file> [diff_spec]}"
diff_spec="${2:-HEAD~1 HEAD}"

if [[ ! -f "$allowlist" ]]; then
    echo "freeze_gate: allowlist file not found: $allowlist" >&2
    exit 2
fi

# Collect patterns, skipping blank lines and comments
patterns=""
while IFS= read -r line; do
    case "$line" in
        ""|"#"*) continue ;;
    esac
    patterns="${patterns}${line}
"
done < "$allowlist"

# The allowlist file itself is always implicitly allowed (it is meta-configuration,
# FROZEN in the pre-registration hash; its own path is never subject to surface checks)
patterns="${patterns}${allowlist}
"

# shellcheck disable=SC2086
changed=$(git diff --name-only $diff_spec)

violations=0
while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    allowed=0
    while IFS= read -r p; do
        [[ -z "$p" ]] && continue
        # In bash case, '*' matches '/', so 'src/*' covers nested paths
        case "$f" in
            $p) allowed=1; break ;;
        esac
    done <<< "$patterns"
    if [[ "$allowed" -eq 0 ]]; then
        echo "freeze_gate: OUT-OF-SURFACE change: $f" >&2
        violations=$((violations + 1))
    fi
done <<< "$changed"

if [[ "$violations" -gt 0 ]]; then
    echo "freeze_gate: FAIL ($violations file(s) outside intervention surface)" >&2
    exit 1
else
    echo "freeze_gate: OK"
    exit 0
fi
