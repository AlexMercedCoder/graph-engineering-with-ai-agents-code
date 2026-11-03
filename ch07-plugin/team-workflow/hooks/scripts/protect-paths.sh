#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "protect-paths: jq is not installed, so this call can't be checked. Install jq." >&2; exit 2; }

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // ""') || { echo "protect-paths: couldn't read the hook input, so the call is refused." >&2; exit 2; }
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

case "$tool" in
  Write|Edit) ;;
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
