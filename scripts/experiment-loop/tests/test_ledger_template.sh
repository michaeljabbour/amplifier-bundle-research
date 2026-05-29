#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$HERE/../../../templates/experiment-ledger.yaml"

if ! test -f "$TEMPLATE"; then
    echo "FAIL: template missing"
    exit 1
fi

if python3 -c 'import yaml' 2>/dev/null; then
    if ! python3 -c "import yaml; yaml.safe_load(open('$TEMPLATE')); print('yaml-parse-ok')"; then
        echo "FAIL: template is not valid YAML"
        exit 1
    fi
else
    for key in "iteration:" "prereg_hash:" "intervention:" "primary_metric:" "decision:" "label:"; do
        if ! grep -q "$key" "$TEMPLATE"; then
            echo "FAIL: template missing key $key"
            exit 1
        fi
    done
    echo "grep-structural-ok"
fi

echo "PASS: ledger_template"
exit 0
