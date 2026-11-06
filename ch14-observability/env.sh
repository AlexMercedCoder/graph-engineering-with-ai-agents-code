# Source this in the shell you start Claude Code from, with collector.py running.
# Claude Code ignores these variables in a repository's .claude/settings.json;
# set them in your shell, in ~/.claude/settings.json, or in managed settings.
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1      # traces are still beta
export OTEL_TRACES_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:8814
# Real skill, agent, and MCP tool names, which the triage reads. It also sends Bash
# commands and tool input; collector.py drops those by name.
export OTEL_LOG_TOOL_DETAILS=1

# Short sessions: export metrics every 2 seconds instead of every 60.
# export OTEL_METRIC_EXPORT_INTERVAL=2000

# Content stays off. Turn these on only in development, with synthetic data:
# export OTEL_LOG_USER_PROMPTS=1
# export OTEL_LOG_TOOL_CONTENT=1

# Hook spans need detailed beta tracing as well (debugging only; high volume):
# export ENABLE_BETA_TRACING_DETAILED=1
# export BETA_TRACING_ENDPOINT=http://127.0.0.1:8814
