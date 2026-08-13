#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "confirm-destructive-sql: jq not installed, hook skipped" >&2; exit 0; }

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

if [[ "$cmd" == *"DROP TABLE"* || "$cmd" == *"TRUNCATE"* || "$cmd" == *"DELETE FROM"* ]]; then
  cat <<JSON
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This command modifies or removes table data. Review it before it runs."
  }
}
JSON
  exit 0
fi

exit 0
