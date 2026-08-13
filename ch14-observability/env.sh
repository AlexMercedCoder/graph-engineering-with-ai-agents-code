# Source this before starting your harness, with Jaeger running from docker-compose.
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1

# Content logging stays off. Chapter 14's defensible default is metadata always,
# content never in production, content selectively in development with synthetic data.
# export OTEL_LOG_USER_PROMPTS=1
