#!/usr/bin/env bash
# Feed hooks/audit-trace.sh commands that carry fake secrets and check that none
# reaches the audit log. Add a line here for every token format your team uses.
set -euo pipefail
hook=$(cd "$(dirname "$0")/.." && pwd)/hooks/audit-trace.sh
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
for cmd in 'export OPENAI_API_KEY=sk-test1234567890abcdef && make' \
           'curl -H "Authorization: Bearer test.abc123def456" https://example.com' \
           'mysql --password hunter2-test -h db' \
           'git push https://x:ghp_test1234567890abcdef@github.com/o/r' \
           'aws s3 ls # AKIATESTTESTTESTTEST'; do
  jq -n --arg c "$cmd" '{session_id:"s", hook_event_name:"PreToolUse", tool_name:"Bash",
                         tool_use_id:"t", tool_input:{command:$c}}' | (cd "$d" && bash "$hook")
done
if grep -E 'sk-test|test\.abc123|hunter2|ghp_test|AKIATEST' "$d/.agent-work/audit.jsonl"; then
  echo "a fake secret reached the audit log" >&2; exit 1
fi
echo "redaction ok ($(wc -l < "$d/.agent-work/audit.jsonl") commands)"
