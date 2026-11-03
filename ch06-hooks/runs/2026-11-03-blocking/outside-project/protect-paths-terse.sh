#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "protect-paths: jq is not installed, so this call can't be checked. Install jq." >&2; exit 2; }

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // ""')
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

case "$tool" in
  Write|Edit|MultiEdit) ;;
  *) exit 0 ;;
esac

for guarded in "migrations/" ".env" "package-lock.json" "terraform/"; do
  if [[ "$path" == *"$guarded"* ]]; then
    echo "Blocked." >&2
    exit 2
  fi
done

exit 0
