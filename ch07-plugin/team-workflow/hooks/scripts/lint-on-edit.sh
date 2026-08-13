#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

[[ "$path" == *.js ]] || exit 0
[[ -f "$path" ]] || exit 0

# The sample project ships a dependency-free formatter. If you are using eslint
# and prettier instead, swap the next line for your own invocation.
if [[ -f scripts/lint.js ]]; then
  node scripts/lint.js --fix "$path" >/dev/null 2>&1 || true
fi

exit 0
