#!/usr/bin/env bash
# Ask an agent Chapter 11's six questions through the remote connector, signed in
# as one identity, with the plugin's skill loaded, and grade the transcript.
#
#   python3 connector/server.py &                       # in another terminal
#   bash eval/run-agents.sh claude|opencode <identity> <transcript.jsonl>
#
# The access token comes from tools/connector-check.py --token, which signs in
# through the connector's OAuth flow. Claude Code loads the plugin folder with
# --plugin-dir and reaches the connector through --mcp-config, so the plugin's
# placeholder URL is never used; OpenCode gets the skill copied into the run
# folder and a remote MCP entry. Nothing from your user configuration joins the
# run (--setting-sources project,local and --strict-mcp-config for Claude Code).
set -euo pipefail
harness=${1:?usage: run-agents.sh claude|opencode <identity> <transcript>}
identity=${2:?usage}
out=$(realpath -m "${3:?usage}")
here=$(cd "$(dirname "$0")/.." && pwd)
ch11="$here/../ch11-catalog"
plugin="$here/marketplace/plugins/governed-data"
url=http://127.0.0.1:8813/mcp
d=$(mktemp -d)
trap 'rm -rf "$d"' EXIT    # the folder holds a live access token until the run ends
mkdir -p "$(dirname "$out")"

token=$(python3 "$here/tools/connector-check.py" --token "$identity")
questions=$(python3 -c "
import json, sys
for l in open(sys.argv[1]):
    if l.strip():
        q = json.loads(l); print(f\"{q['id'][1:]}. {q['question']}\")" "$ch11/eval/questions.jsonl")
prompt="Answer these six business questions about our insurance company. Company data is available through the governed-data tools.

$questions

When you are done, end your reply with one JSON object, keys q1 to q6. Each value is a number, an object mapping each category to a number, or a string that starts with REFUSED: and gives the reason, when the question can't be answered from the data you have."

case "$harness" in
  claude)
    printf '{"mcpServers": {"governed-data": {"type": "http", "url": "%s", "headers": {"Authorization": "Bearer %s"}}}}\n' \
      "$url" "$token" > "$d/mcp.json"
    (cd "$d" && claude -p "$prompt" --plugin-dir "$plugin" --setting-sources project,local \
      --mcp-config "$d/mcp.json" --strict-mcp-config --allowedTools mcp__governed-data Skill \
      --disallowedTools Bash --output-format stream-json --verbose --max-turns 40 \
      < /dev/null > "$out" 2>/dev/null) || true ;;
  opencode)
    mkdir -p "$d/.opencode/skills" && cp -r "$plugin/skills/answer-with-governed-data" "$d/.opencode/skills/"
    cat > "$d/opencode.json" <<JSON
{"\$schema": "https://opencode.ai/config.json",
 "mcp": {"governed-data": {"type": "remote", "url": "$url", "oauth": false,
                           "headers": {"Authorization": "Bearer {env:GOVERNED_DATA_TOKEN}"}}},
 "permission": {"bash": "deny", "skill": {"*": "deny", "answer-with-governed-data": "allow"}}}
JSON
    (cd "$d" && GOVERNED_DATA_TOKEN="$token" opencode run --format json ${OPENCODE_MODEL:+-m "$OPENCODE_MODEL"} \
      "$prompt" < /dev/null > "$out" 2>/dev/null) || true ;;
  *) echo "unknown harness: $harness" >&2; exit 1 ;;
esac
python3 "$ch11/eval/grade.py" "$out"
