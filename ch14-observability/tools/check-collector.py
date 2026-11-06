#!/usr/bin/env python3
"""Send one span through collector.py and check what it stored.

    python3 collector.py --out /tmp/x &      # then
    python3 tools/check-collector.py /tmp/x  # prints "collector ok" or fails

The span carries an email address and a prompt attribute; the stored copy must
hold a hash instead of the address and no prompt.
"""
import json
import logging
import sys
import time
from pathlib import Path

logging.disable(logging.CRITICAL)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # noqa: E402
from opentelemetry.sdk.resources import Resource  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: E402

out = Path(sys.argv[1])
provider = TracerProvider(resource=Resource.create({"service.name": "check"}))
provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://127.0.0.1:8814/v1/traces")))
with provider.get_tracer("check").start_as_current_span("claude_code.tool") as span:
    span.set_attributes({"user.email": "dev@example.com", "user_prompt": "secret plan", "tool_name": "Read"})
provider.shutdown()
time.sleep(0.5)
stored = [json.loads(l) for l in (out / "spans.jsonl").open()]
a = [s for s in stored if s["resource"].get("service.name") == "check"][-1]["attributes"]
assert a["user.email"].startswith(("sha256:", "hmac:")) and "example.com" not in json.dumps(a), a
assert "user_prompt" not in a and a["tool_name"] == "Read", a
print("collector ok")
