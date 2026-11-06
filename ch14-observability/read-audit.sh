#!/usr/bin/env bash
# The no-tracing substitute: answer the route question from the Chapter 6 audit log.
#   bash read-audit.sh [.agent-work/audit.jsonl]
set -euo pipefail
LOG="${1:-.agent-work/audit.jsonl}"
[[ -f "$LOG" ]] || { echo "no audit log at $LOG. Enable the Chapter 6 audit hook first." >&2; exit 1; }
command -v jq >/dev/null || { echo "needs jq" >&2; exit 1; }

echo "== calls per session, agent, and tool (PreToolUse only, so each call counts once)"
jq -r 'select(.event == "PreToolUse") | "\(.session[0:8])  \(.agent)  \(.tool)"' "$LOG" | sort | uniq -c
echo; echo "== skills loaded"
jq -r 'select(.event == "PreToolUse" and .tool == "Skill") | .target // "(name not logged)"' "$LOG" | sort | uniq -c
echo; echo "== MCP tools called"
jq -r 'select(.event == "PreToolUse" and (.tool | startswith("mcp__"))) | .tool' "$LOG" | sort | uniq -c
