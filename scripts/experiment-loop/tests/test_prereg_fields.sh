#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREREG="$HERE/../../../templates/preregistration.yaml"

if ! test -f "$PREREG"; then
  echo "FAIL: prereg missing"; exit 1
fi

for key in \
  intervention_surface \
  measurement_protocol \
  judge_panel \
  meta_reviewer \
  kappa_threshold \
  primary_metric \
  guardrail_metrics \
  stopping_rule \
  max_iterations \
  patience \
  budget \
  seeds \
  held_out_confirmation
do
  if ! grep -q "$key" "$PREREG"; then
    echo "FAIL: prereg missing field: $key"; exit 1
  fi
done

echo "PASS: prereg_fields"; exit 0
