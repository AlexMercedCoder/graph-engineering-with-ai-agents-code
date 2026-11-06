#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
mkdir -p .agent-work
printf '%s' "$input" | jq -c '
  def redact:
    if type != "string" then . else
      gsub("(?<k>(?i)authorization:\\s*(bearer|basic|token)\\s+)[^\\s\"'\'']+"; "\(.k)[REDACTED]")
      | gsub("(?<k>(?i)(password|passwd|token|secret|api[-_]?key)[=:]\\s*)[^\\s&\"'\'']+"; "\(.k)[REDACTED]")
      | gsub("(?<k>(?i)--(password|token|secret|api-key)[= ])[^\\s\"'\'']+"; "\(.k)[REDACTED]")
      | gsub("(?<k>(^|\\s)(-u|--user)[= ]?[^\\s:]+:)[^\\s\"'\'']+"; "\(.k)[REDACTED]")
      | gsub("(?<k>://[^/\\s:@]+:)[^@\\s/]+@"; "\(.k)[REDACTED]@")
      | gsub("(sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,})"; "[REDACTED]")
    end;
  {
    ts: (now | todate),
    session: .session_id,
    event: .hook_event_name,
    agent: (.agent_type // "main"),
    tool: .tool_name,
    id: .tool_use_id,
    target: ((.tool_input.file_path // .tool_input.command // .tool_input.pattern // .tool_input.description // null) | redact)
  }' >> .agent-work/audit.jsonl

exit 0
