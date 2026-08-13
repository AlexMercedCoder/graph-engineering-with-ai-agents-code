#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "guard-bash: jq not installed, hook skipped" >&2; exit 0; }

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

deny() {
  echo "Blocked: $1" >&2
  echo "$2" >&2
  exit 2
}

case "$cmd" in
  *"rm -rf"*)            deny "recursive delete" "Delete specific files by name, or ask the user." ;;
  *"git push"*)          deny "push to remote" "Commit locally and let the user push." ;;
  *"git reset --hard"*)  deny "hard reset" "Use git stash to set changes aside instead." ;;
  *"chmod 777"*)         deny "world-writable permissions" "Grant the narrowest mode the task needs." ;;
  *"curl"*"| sh"*)       deny "piping a download to a shell" "Download, inspect, then run explicitly." ;;
esac

exit 0
