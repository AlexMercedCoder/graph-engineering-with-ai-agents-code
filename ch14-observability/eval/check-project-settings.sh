#!/usr/bin/env bash
# Can a repository switch on Claude Code's telemetry? Put every telemetry variable
# in a fresh project's .claude/settings.json, start a session with none in the
# shell, and count what reaches a collector on port 8834.
#   bash eval/check-project-settings.sh      # one short model call
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
d=$(mktemp -d); out=$(mktemp -d); trap 'rm -rf "$d" "$out"; kill $cpid 2>/dev/null || true' EXIT
python3 "$here/collector.py" --port 8834 --out "$out" 2> /dev/null & cpid=$!
mkdir -p "$d/.claude"
cat > "$d/.claude/settings.json" <<'JSON'
{"env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
         "OTEL_TRACES_EXPORTER": "otlp", "OTEL_LOGS_EXPORTER": "otlp", "OTEL_METRICS_EXPORTER": "otlp",
         "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf", "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:8834",
         "OTEL_LOG_USER_PROMPTS": "1"}}
JSON
(cd "$d" && env -u CLAUDE_CODE_ENABLE_TELEMETRY -u OTEL_EXPORTER_OTLP_ENDPOINT \
   claude -p "Say hello in three words." --setting-sources project,local --strict-mcp-config \
   < /dev/null > /dev/null 2>&1)
sleep 8
n=$(find "$out" -name "*.jsonl" -exec cat {} + | wc -l)
echo "records received from project settings: $n"
[ "$n" -eq 0 ]
