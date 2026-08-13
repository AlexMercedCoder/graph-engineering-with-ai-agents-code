#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
mkdir -p .agent-work
printf '%s\n' "$(printf '%s' "$input" | jq -c --arg run "${AGENT_RUN_ID:-local}" '{
  ts: (now | todate),
  run: $run,
  agent: (.agent_type // "main"),
  parent: (.agent_id // "main"),
  tool: .tool_name,
  target: (.tool_input.file_path // .tool_input.command // null)
}')" >> .agent-work/audit.jsonl

exit 0
