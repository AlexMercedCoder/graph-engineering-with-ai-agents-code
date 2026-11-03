#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "confirm-destructive-sql: jq is not installed, so this call can't be checked. Install jq." >&2; exit 2; }

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""') || { echo "confirm-destructive-sql: couldn't read the hook input, so the call is refused." >&2; exit 2; }

shopt -s nocasematch
if [[ "$cmd" =~ (drop[[:space:]]+table|truncate|delete[[:space:]]+from) ]]; then
  cat <<JSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This command modifies or removes table data. Review it before it runs."
  }
}
JSON
fi

exit 0
