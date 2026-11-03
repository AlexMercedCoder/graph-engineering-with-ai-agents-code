#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
mkdir -p .agent-work
printf '%s' "$input" | jq -c '{
  ts: (now | todate),
  session: .session_id,
  event: .hook_event_name,
  agent: (.agent_type // "main"),
  tool: .tool_name,
  target: (.tool_input.file_path // .tool_input.command // .tool_input.pattern // .tool_input.description // null)
}' >> .agent-work/audit.jsonl

exit 0
