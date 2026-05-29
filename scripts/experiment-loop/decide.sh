#!/usr/bin/env bash
set -uo pipefail
decision="${1:?usage: decide.sh <keep|revert>}"
case "$decision" in
  keep)
    echo "decide: keep (intervention retained)"
    exit 0
    ;;
  revert)
    git reset --hard HEAD~1
    echo "decide: revert (intervention commit dropped)"
    exit 0
    ;;
  *)
    echo "decide: invalid decision '$decision' (want keep|revert)" >&2
    exit 2
    ;;
esac
