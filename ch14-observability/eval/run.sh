#!/usr/bin/env bash
# One traced session: a fresh folder, the collector, the graph server, one harness.
#
#   bash eval/run.sh claude|opencode <condition> <run-dir>
#
#   baseline           the blast-radius skill and the graph server as published
#   bad-description    the skill's description rewritten for release notes (execution graph)
#   depth-cap-silent   the server's depth cap lowered to 1, and its reply doesn't
#                      mention partial coverage (knowledge graph)
#   depth-cap          the same cap, with the server's partial-coverage line
#   soft-body          the skill body asks for direct dependents only
#   stale-rule         the skill body tells the agent to leave two services out (reasoning)
#
# ROLE=sre|contractor picks the access token (default sre); QUESTION replaces the question.
# Writes <run-dir>/telemetry/{spans,logs,metrics}.jsonl and <run-dir>/transcript.jsonl,
# then runs eval/triage.py on it. Uses ports 8814 (collector), 8815 (graph server),
# and 4817 (OpenCode's server); PORT_OFFSET=10 moves all three up by 10, so two
# runs can go at once. Set OPENCODE_MODEL to pick OpenCode's model.
set -euo pipefail
harness=${1:?usage: run.sh claude|opencode <condition> <run-dir>}
condition=${2:?usage}
out=$(realpath -m "${3:?usage}")
here=$(cd "$(dirname "$0")/.." && pwd)
question=${QUESTION:-"Which services are affected if UserService changes?"}
role=${ROLE:-sre}
off=${PORT_OFFSET:-0}
cport=$((8814 + off)); gport=$((8815 + off)); oport=$((4817 + off))
# Test tokens last eight hours; make new ones when they're missing or expired.
python3 -c "import json,sys,time; t=json.load(open(sys.argv[1])); sys.exit(min(v['exp'] for v in t.values()) < time.time() + 600)" \
  "$here/config/test-tokens.json" 2> /dev/null || python3 "$here/tools/make-test-tokens.py" > /dev/null
[ -f "$here/../ch10-graph/graph/project-graph.db" ] || (cd "$here/../ch10-graph/graph" && python3 extract.py > /dev/null)
set -a; . "$here/config/test-tokens.env"; set +a
export GRAPH_TOKEN; GRAPH_TOKEN=$(eval echo "\$GRAPH_TOKEN_${role^^}")

skill=blast-radius; server_env=()
case "$condition" in
  baseline) ;;
  bad-description) skill=blast-radius-bad-description ;;
  soft-body) skill=blast-radius-soft-body ;;
  stale-rule) skill=blast-radius-stale-rule ;;
  depth-cap) server_env=(GRAPH_MAX_DEPTH=1) ;;
  depth-cap-silent) server_env=(GRAPH_MAX_DEPTH=1 GRAPH_REPORT_COVERAGE=0) ;;
  *) echo "unknown condition: $condition" >&2; exit 1 ;;
esac

d=$(mktemp -d)
mkdir -p "$out/telemetry" "$d/.claude/skills/blast-radius"
cp "$here/eval/skills/$skill/SKILL.md" "$d/.claude/skills/blast-radius/SKILL.md"
pids=()
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT

# COLLECT=production runs the collector as the chapter recommends for production:
# content dropped, internal spans reduced to their IDs. The default keeps content,
# for development with the synthetic graph.
collect=(--keep-content); [ "${COLLECT:-}" = production ] && collect=(--agent-spans-only)
python3 "$here/collector.py" --port "$cport" --out "$out/telemetry" "${collect[@]}" 2> /dev/null & pids+=($!)
(cd "$here/server" && exec env "${server_env[@]}" GRAPH_PORT="$gport" COLLECTOR="http://127.0.0.1:$cport" \
   python3 graph_server.py 2> "$out/server-stderr.txt") & pids+=($!)
sleep 3

otel=(CLAUDE_CODE_ENABLE_TELEMETRY=1 CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
      OTEL_TRACES_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp OTEL_METRICS_EXPORTER=otlp
      OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:$cport
      OTEL_LOG_TOOL_DETAILS=1 OTEL_METRIC_EXPORT_INTERVAL=2000)
case "$harness" in
  claude)
    cat > "$d/mcp.json" <<JSON
{"mcpServers": {"project-graph": {"type": "http", "url": "http://127.0.0.1:$gport/mcp",
  "headers": {"Authorization": "Bearer \${GRAPH_TOKEN}"}}}}
JSON
    (cd "$d" && env "${otel[@]}" claude -p "$question" --model claude-opus-5-5 \
       --setting-sources project,local --strict-mcp-config --mcp-config mcp.json \
       --allowedTools mcp__project-graph Skill --output-format stream-json --verbose \
       --max-turns 20 < /dev/null > "$out/transcript.jsonl" 2> /dev/null) || true ;;
  opencode)
    cat > "$d/opencode.json" <<JSON
{"\$schema": "https://opencode.ai/config.json", "experimental": {"openTelemetry": true},
 "mcp": {"project-graph": {"type": "remote", "url": "http://127.0.0.1:$gport/mcp", "oauth": false,
   "headers": {"Authorization": "Bearer {env:GRAPH_TOKEN}"}}},
 "permission": {"bash": "deny", "edit": "deny", "webfetch": "deny",
   "skill": {"*": "deny", "blast-radius": "allow"}}}
JSON
    # A long-lived server flushes its spans; a bare `opencode run` can exit first.
    (cd "$d" && OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:$cport" exec opencode serve --port "$oport" \
       > /dev/null 2>&1) & pids+=($!)
    sleep 4
    (cd "$d" && opencode run --attach "http://127.0.0.1:$oport" --dir "$d" --format json \
       ${OPENCODE_MODEL:+-m "$OPENCODE_MODEL"} "$question" < /dev/null \
       > "$out/transcript.jsonl" 2> /dev/null) || true ;;
  *) echo "unknown harness: $harness" >&2; exit 1 ;;
esac
sleep 8   # let every exporter flush
cleanup; trap - EXIT
printf '{"harness": "%s", "condition": "%s", "role": "%s"}\n' "$harness" "$condition" "$role" > "$out/run.json"
python3 "$here/eval/triage.py" "$out"
