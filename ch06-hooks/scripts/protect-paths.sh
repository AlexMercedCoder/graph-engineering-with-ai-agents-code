#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "protect-paths: jq not installed, hook skipped" >&2; exit 0; }

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // ""')
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

case "$tool" in
  Write|Edit|MultiEdit) ;;
  *) exit 0 ;;
esac

for guarded in "migrations/" ".env" "package-lock.json" "terraform/"; do
  if [[ "$path" == *"$guarded"* ]]; then
    echo "Blocked write to $path. Paths matching $guarded require human review." >&2
    echo "Describe the change you need and ask the user to make it." >&2
    exit 2
  fi
done

exit 0
