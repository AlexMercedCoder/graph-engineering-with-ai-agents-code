#!/usr/bin/env bash
# The blast-radius question with no telemetry at all: the trace-ready audit hook
# records the harness side, GRAPH_AUDIT_LOG records the server side.
#
#   bash eval/run-notrace.sh <run-dir>
#
# Writes <run-dir>/audit.jsonl, graph-audit.jsonl, and transcript.jsonl, then
# prints read-audit.sh's report. PORT_OFFSET works as in run.sh.
set -euo pipefail
out=$(realpath -m "${1:?usage: run-notrace.sh <run-dir>}")
here=$(cd "$(dirname "$0")/.." && pwd)
off=${PORT_OFFSET:-0}; gport=$((8815 + off))
# Test tokens last eight hours; make new ones when they're missing or expired.
python3 -c "import json,sys,time; t=json.load(open(sys.argv[1])); sys.exit(min(v['exp'] for v in t.values()) < time.time() + 600)" \
  "$here/config/test-tokens.json" 2> /dev/null || python3 "$here/tools/make-test-tokens.py" > /dev/null
set -a; . "$here/config/test-tokens.env"; set +a
export GRAPH_TOKEN=$GRAPH_TOKEN_SRE
d=$(mktemp -d); mkdir -p "$out" "$d/.claude/skills/blast-radius" "$d/.claude/hooks"
cp "$here/eval/skills/blast-radius/SKILL.md" "$d/.claude/skills/blast-radius/"
cp "$here/hooks/audit-trace.sh" "$d/.claude/hooks/"
cat > "$d/.claude/settings.json" <<'JSON'
{"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command",
   "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/audit-trace.sh", "timeout": 5}]}]}}
JSON
cat > "$d/mcp.json" <<JSON
{"mcpServers": {"project-graph": {"type": "http", "url": "http://127.0.0.1:$gport/mcp",
  "headers": {"Authorization": "Bearer \${GRAPH_TOKEN}"}}}}
JSON
(cd "$here/server" && GRAPH_PORT=$gport COLLECTOR=http://127.0.0.1:9 \
   GRAPH_AUDIT_LOG="$out/graph-audit.jsonl" exec python3 graph_server.py 2> /dev/null) & spid=$!
trap 'kill $spid 2>/dev/null || true' EXIT
sleep 3
(cd "$d" && claude -p "Which services are affected if UserService changes?" --model claude-opus-5-5 \
   --setting-sources project,local --strict-mcp-config --mcp-config mcp.json \
   --allowedTools mcp__project-graph Skill --output-format stream-json --verbose \
   < /dev/null > "$out/transcript.jsonl" 2> /dev/null) || true
cp "$d/.agent-work/audit.jsonl" "$out/audit.jsonl"
bash "$here/read-audit.sh" "$out/audit.jsonl"
echo; echo "== server record"
jq -c '{ts, tool, "graph.root", "graph.paths_found", "graph.coverage", "graph.subject"}' "$out/graph-audit.jsonl"
