#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT="$HERE/../../../agents/experiment-runner.md"

if ! test -f "$AGENT"; then
  echo "FAIL: agents/experiment-runner.md does not exist"; exit 1
fi

python3 - "$AGENT" <<'EOF'
import sys, yaml

path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    text = fh.read()

parts = text.split("---")
if len(parts) < 3:
    print("FAIL: no frontmatter found"); sys.exit(1)

fm = yaml.safe_load(parts[1])
meta = fm.get("meta", {})

if meta.get("name") != "experiment-runner":
    print(f"FAIL: meta.name={meta.get('name')!r}, expected 'experiment-runner'"); sys.exit(1)

if fm.get("model_role") != "reasoning":
    print(f"FAIL: model_role={fm.get('model_role')!r}, expected 'reasoning'"); sys.exit(1)

if "common-agent-base.md" not in text:
    print("FAIL: 'common-agent-base.md' not found in agent file"); sys.exit(1)

print("frontmatter-ok")
EOF

echo "PASS: experiment_runner_agent"; exit 0
