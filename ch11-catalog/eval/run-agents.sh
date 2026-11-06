#!/usr/bin/env bash
# Ask an agent the six questions in eval/questions.jsonl under one of four settings,
# in a fresh folder, and save the transcript for eval/grade.py.
#
#   bash eval/run-agents.sh claude|opencode raw|rawhook|catalog|tools|skill <transcript.jsonl>
#
#   raw      warehouse.db and schema.sql; the agent writes SQL with the sqlite3 command
#   rawhook  raw, plus hooks/validate-sql.py as a PreToolUse hook (Claude Code only)
#   catalog  the same, plus catalog.yaml to read before writing SQL
#   tools    no database file; the governed-data MCP server as identity analyst
#   skill    tools, plus the answer-with-governed-data skill
#
# Claude Code runs with --setting-sources project,local and --strict-mcp-config, so
# nothing from your user configuration joins the run. OpenCode gets an opencode.json
# in the run folder. Set OPENCODE_MODEL (for example openai/gpt-6.1-sol) to pick its model.
set -euo pipefail
harness=${1:?usage: run-agents.sh claude|opencode raw|catalog|tools|skill <transcript>}
setting=${2:?usage}
out=$(realpath -m "${3:?usage}")
here=$(cd "$(dirname "$0")/.." && pwd)
[ -f "$here/warehouse/warehouse.db" ] || python3 "$here/warehouse/seed.py" > /dev/null
d=$(mktemp -d)
mkdir -p "$(dirname "$out")"

questions=$(python3 -c "
import json, sys
for l in open(sys.argv[1]):
    if l.strip():
        q = json.loads(l); print(f\"{q['id'][1:]}. {q['question']}\")" "$here/eval/questions.jsonl")
case "$setting" in
  raw|rawhook|catalog)
    cp "$here/warehouse/warehouse.db" "$d/"
    python3 "$here/warehouse/seed.py" --schema > "$d/schema.sql"
    where="The company warehouse is the SQLite database warehouse.db in this folder, and schema.sql has its table definitions. Query it with the sqlite3 command."
    if [ "$setting" = rawhook ]; then
      [ "$harness" = claude ] || { echo "rawhook needs Claude Code" >&2; exit 1; }
      mkdir -p "$d/.claude"
      python3 -c 'import sys; t = open(sys.argv[1]).read()
print(t.replace(chr(92) + chr(34) + "$CLAUDE_PROJECT_DIR" + chr(92) + chr(34), sys.argv[2]), end="")' \
        "$here/hooks/settings.example.json" "$here" > "$d/.claude/settings.json"
    fi
    if [ "$setting" = catalog ]; then
      cp "$here/catalog.yaml" "$d/"
      where="$where catalog.yaml is the semantic model the data team maintains; read it before writing SQL."
    fi ;;
  tools|skill)
    where="Company data is available through the governed-data tools."
    if [ "$setting" = skill ]; then
      mkdir -p "$d/.claude/skills"; cp -r "$here/skills/answer-with-governed-data" "$d/.claude/skills/"
    fi ;;
  *) echo "unknown setting: $setting" >&2; exit 1 ;;
esac

prompt="Answer these six business questions about our insurance company. $where

$questions

When you are done, end your reply with one JSON object, keys q1 to q6. Each value is a number, an object mapping each category to a number, or a string that starts with REFUSED: and gives the reason, when the question can't be answered from the data you have."

env_json='{"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}'
case "$harness" in
  claude)
    args=(--setting-sources project,local --strict-mcp-config --output-format stream-json --verbose --max-turns 40)
    if [ "$setting" = raw ] || [ "$setting" = rawhook ] || [ "$setting" = catalog ]; then
      args+=(--allowedTools "Bash(sqlite3:*)" Read)
    else
      cat > "$d/mcp.json" <<JSON
{"mcpServers": {"governed-data": {"command": "python3", "args": ["$here/server/server.py"], "env": $env_json}}}
JSON
      args+=(--mcp-config "$d/mcp.json" --allowedTools mcp__governed-data Skill --disallowedTools Bash)
    fi
    (cd "$d" && claude -p "$prompt" "${args[@]}" < /dev/null > "$out" 2>/dev/null) || true ;;
  opencode)
    if [ "$setting" = raw ] || [ "$setting" = catalog ]; then
      echo '{"$schema": "https://opencode.ai/config.json", "permission": {"skill": {"*": "deny"}}}' > "$d/opencode.json"
    else
      cat > "$d/opencode.json" <<JSON
{"\$schema": "https://opencode.ai/config.json",
 "mcp": {"governed-data": {"type": "local", "command": ["python3", "$here/server/server.py"], "environment": $env_json}},
 "permission": {"bash": "deny", "skill": {"*": "deny", "answer-with-governed-data": "allow"}}}
JSON
    fi
    (cd "$d" && opencode run --format json ${OPENCODE_MODEL:+-m "$OPENCODE_MODEL"} "$prompt" < /dev/null > "$out" 2>/dev/null) || true ;;
  *) echo "unknown harness: $harness" >&2; exit 1 ;;
esac
python3 "$here/eval/grade.py" "$out"
