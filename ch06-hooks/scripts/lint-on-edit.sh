#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "lint-on-edit: jq not installed, hook skipped" >&2; exit 0; }

input=$(cat)
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

[[ "$path" == *.js && -f "$path" ]] || exit 0

node scripts/lint.js --fix "$path" >/dev/null 2>&1 || true

if [[ "$path" == */src/services/* ]]; then
  hit=$(grep -nE "from ['\"]\.\./db\.js['\"]" "$path" || true)
  if [[ -n "$hit" ]]; then
    echo "$path still imports from src/db.js (line ${hit%%:*})." >&2
    echo "Project rule: a file you edit in src/services/ must get all its data through" >&2
    echo "the repository classes in src/repositories/, with no import from src/db.js," >&2
    echo "including for functions your task didn't touch. Add a repository method if one is missing." >&2
    exit 2
  fi
fi

exit 0
