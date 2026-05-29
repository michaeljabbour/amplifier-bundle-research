#!/usr/bin/env bash
# deterministic stand-in for a frozen measurement run_command
# emits one parseable primary metric line
# no API/network/randomness so keep/revert is deterministic
echo "seed: ${SEED:-0}"
echo "primary_metric: 0.42"
