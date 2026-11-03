#!/usr/bin/env bash
# Runs the agent, then the checks a Stop hook would have run.
set -euo pipefail

claude -p "$@" --permission-mode acceptEdits

node scripts/lint.js --fix >/dev/null 2>&1 || true
npm test || {
  echo "The agent finished but the tests do not pass."
  exit 1
}
