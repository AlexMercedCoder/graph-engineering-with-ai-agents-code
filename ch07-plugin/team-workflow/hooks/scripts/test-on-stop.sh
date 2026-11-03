#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "test-on-stop: jq not installed, hook skipped" >&2; exit 0; }

input=$(cat)
session=$(printf '%s' "$input" | jq -r '.session_id // "local"')

[[ -n "$(git status --porcelain -- src tests 2>/dev/null)" ]] || exit 0

mkdir -p .agent-work
counter=".agent-work/stop-attempts-$session"
log=".agent-work/stop-tests.log"

if npm test --silent >"$log" 2>&1; then
  rm -f "$counter"
  exit 0
fi

attempts=$(( $(cat "$counter" 2>/dev/null || echo 0) + 1 ))
echo "$attempts" > "$counter"
if (( attempts >= 3 )); then
  rm -f "$counter"
  echo "Tests still fail after $attempts tries. Stopping; tell the user what is still broken." >&2
  exit 0
fi

echo "The tests fail, and you changed files under src/ or tests/, so the work isn't done." >&2
echo "Fix the failures below, then finish. Failing output:" >&2
grep -E "^not ok|AssertionError|expected|actual" "$log" | head -n 20 >&2 || tail -n 20 "$log" >&2
exit 2
