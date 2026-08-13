#!/usr/bin/env bash
# The no-tracing substitute: the Chapter 6 audit log answers the same questions.
set -euo pipefail
LOG="${1:-.agent-work/audit.jsonl}"
[[ -f "$LOG" ]] || { echo "no audit log at $LOG. Enable the Chapter 6 audit hook first." >&2; exit 1; }
command -v jq >/dev/null || { echo "needs jq" >&2; exit 1; }

echo "== tool calls by tool"
jq -r '.tool' "$LOG" | sort | uniq -c | sort -rn
echo; echo "== calls by agent (which worker did what)"
jq -r '.agent' "$LOG" | sort | uniq -c | sort -rn
echo; echo "== files touched"
jq -r 'select(.target != null) | .target' "$LOG" | sort -u | head -20
