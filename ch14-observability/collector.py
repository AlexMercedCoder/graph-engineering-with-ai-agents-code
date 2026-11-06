#!/usr/bin/env python3
"""A local OTLP/HTTP receiver: no Docker, no account.

    python3 collector.py                 # listens on http://127.0.0.1:8814
    python3 collector.py --out telemetry/run-1

Accepts traces, logs, and metrics on /v1/traces, /v1/logs, and /v1/metrics,
as protobuf or JSON, and appends one JSON line per span, log record, or metric
data point to spans.jsonl, logs.jsonl, and metrics.jsonl in the output folder.

The collector is also where redaction belongs. Before anything is written,
identity attributes are pseudonymized (user.email becomes a hash, so audit
queries can still group by person) and the content attributes in DROP are
removed, whatever the harness was configured to send. DROP matches exact
attribute keys: prompts, responses, tool input and output, Bash commands,
and OpenCode's ai.* content.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

PSEUDONYMIZE = {"user.email", "user.id", "user.account_uuid", "user.account_id", "organization.id",
                "session.id"}
DROP = {"user_prompt", "prompt", "response", "new_context", "tool_input", "tool_parameters",
        "full_command", "bash_command", "content", "diff", "system_prompt_preview",
        "system_reminders", "response.model_output", "gen_ai.input.messages",
        "gen_ai.output.messages", "gen_ai.system_instructions", "body", "ai.prompt",
        "ai.prompt.messages", "ai.response.text", "ai.response.toolCalls", "ai.toolCall.args",
        "ai.toolCall.result"}
REQUESTS = {"/v1/traces": ExportTraceServiceRequest, "/v1/logs": ExportLogsServiceRequest,
            "/v1/metrics": ExportMetricsServiceRequest}


HASH_KEY = os.environ.get("COLLECTOR_HASH_KEY", "").encode()


def pseudonym(v):
    """A short, stable stand-in for an identity. Without COLLECTOR_HASH_KEY it's a
    plain SHA-256, which anyone holding a staff list can reverse by hashing every
    address; set the key in production so only its holder can."""
    if HASH_KEY:
        return "hmac:" + hmac.new(HASH_KEY, str(v).encode(), hashlib.sha256).hexdigest()[:12]
    return "sha256:" + hashlib.sha256(str(v).encode()).hexdigest()[:12]


def value(v):
    """Flatten an OTLP AnyValue (as a dict) into a plain Python value."""
    if not isinstance(v, dict):
        return v
    for key in ("stringValue", "boolValue", "doubleValue"):
        if key in v:
            return v[key]
    if "intValue" in v:
        return int(v["intValue"])
    if "arrayValue" in v:
        return [value(x) for x in v["arrayValue"].get("values", [])]
    if "kvlistValue" in v:
        return attrs(v["kvlistValue"].get("values", []))
    return None


def attrs(kvs, keep_content=False):
    out = {}
    for kv in kvs or []:
        k, v = kv["key"], value(kv.get("value", {}))
        if k == "ai.toolCall.args" and isinstance(v, str):
            try:
                name = json.loads(v).get("name")
            except (ValueError, AttributeError):
                name = None
            if name:
                out["ai.toolCall.skill"] = name   # the skill a skill call loaded; a name, not content
        if k in PSEUDONYMIZE and v:
            v = pseudonym(v)
        if k in DROP and not keep_content:
            continue
        out[k] = v
    return out


def hexid(b64_or_hex):
    """IDs arrive base64-encoded from protobuf and hex-encoded from JSON."""
    if not b64_or_hex:
        return None
    s = b64_or_hex
    if len(s) in (16, 32) and all(c in "0123456789abcdefABCDEF" for c in s):
        return s.lower()
    import base64
    return base64.b64decode(s).hex()


KEEP_SPANS = ("claude_code.", "SessionPrompt.prompt", "ai.streamText", "ai.toolCall", "Tool.execute",
              "tools/", "graph.", "chat ", "execute_tool", "invoke_agent")


def spans(doc, keep, agent_only=False):
    for rs in doc.get("resourceSpans", []):
        res = attrs(rs.get("resource", {}).get("attributes"), keep)
        for ss in rs.get("scopeSpans", []):
            scope = ss.get("scope", {}).get("name")
            for s in ss.get("spans", []):
                if agent_only and not s.get("name", "").startswith(KEEP_SPANS):
                    # Keep the span's place in the tree, not its contents, so the
                    # kept spans under it can still be joined to their ancestors.
                    yield {"trace_id": hexid(s.get("traceId")), "span_id": hexid(s.get("spanId")),
                           "parent_span_id": hexid(s.get("parentSpanId")), "name": s.get("name"),
                           "start_ns": int(s.get("startTimeUnixNano", 0)),
                           "end_ns": int(s.get("endTimeUnixNano", 0)), "skeleton": True,
                           "status": "STATUS_CODE_UNSET", "attributes": {}, "events": [],
                           "scope": scope, "resource": {"service.name": res.get("service.name")}}
                    continue
                a = attrs(s.get("attributes"), keep)
                if a.get("ai.toolCall.name") != "skill":
                    a.pop("ai.toolCall.skill", None)
                yield {"trace_id": hexid(s.get("traceId")), "span_id": hexid(s.get("spanId")),
                       "parent_span_id": hexid(s.get("parentSpanId")), "name": s.get("name"),
                       "start_ns": int(s.get("startTimeUnixNano", 0)),
                       "end_ns": int(s.get("endTimeUnixNano", 0)),
                       "status": s.get("status", {}).get("code", "STATUS_CODE_UNSET"),
                       "attributes": a,
                       "events": [{"name": e.get("name"), "attributes": attrs(e.get("attributes"), keep)}
                                  for e in s.get("events", [])],
                       "scope": scope, "resource": res}


def logs(doc, keep):
    for rl in doc.get("resourceLogs", []):
        res = attrs(rl.get("resource", {}).get("attributes"), keep)
        for sl in rl.get("scopeLogs", []):
            for r in sl.get("logRecords", []):
                a = attrs(r.get("attributes"), keep)
                yield {"time_ns": int(r.get("timeUnixNano") or r.get("observedTimeUnixNano") or 0),
                       "event": a.get("event.name") or value(r.get("body", {})),
                       "trace_id": hexid(r.get("traceId")), "span_id": hexid(r.get("spanId")),
                       "attributes": a, "resource": res}


def metrics(doc, keep):
    for rm in doc.get("resourceMetrics", []):
        res = attrs(rm.get("resource", {}).get("attributes"), keep)
        for sm in rm.get("scopeMetrics", []):
            for m in sm.get("metrics", []):
                for kind in ("sum", "gauge", "histogram"):
                    for p in m.get(kind, {}).get("dataPoints", []):
                        v = p.get("asDouble", p.get("asInt", p.get("sum")))
                        yield {"name": m.get("name"), "unit": m.get("unit"), "kind": kind,
                               "value": float(v) if v is not None else None,
                               "time_ns": int(p.get("timeUnixNano", 0)),
                               "attributes": attrs(p.get("attributes"), keep), "resource": res}


FLATTEN = {"/v1/traces": ("spans.jsonl", spans), "/v1/logs": ("logs.jsonl", logs),
           "/v1/metrics": ("metrics.jsonl", metrics)}


def handler_for(out: Path, keep_content: bool, agent_only: bool):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            path = self.path.split("?")[0]
            if path not in REQUESTS:
                self.send_error(404)
                return
            body = self.read_body()
            ctype = self.headers.get("Content-Type", "")
            if "json" in ctype:
                doc = json.loads(body or b"{}")
            else:
                msg = REQUESTS[path]()
                msg.ParseFromString(body)
                doc = MessageToDict(msg)
            name, flatten = FLATTEN[path]
            records = flatten(doc, keep_content, agent_only) if path == "/v1/traces" else flatten(doc, keep_content)
            with (out / name).open("a") as f:
                for rec in records:
                    f.write(json.dumps(rec) + "\n")
            reply = REQUESTS[path].__name__.replace("Request", "Response")
            self.send_response(200)
            if "json" in ctype:
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"{}")
            else:
                self.send_header("Content-Type", "application/x-protobuf")
                self.end_headers()

        def read_body(self):
            """OpenCode's JavaScript exporter sends chunked bodies with no Content-Length."""
            if "chunked" not in self.headers.get("Transfer-Encoding", ""):
                return self.rfile.read(int(self.headers.get("Content-Length", 0)))
            chunks = []
            while True:
                size = int(self.rfile.readline().split(b";")[0].strip(), 16)
                if size == 0:
                    self.rfile.readline()
                    return b"".join(chunks)
                chunks.append(self.rfile.read(size))
                self.rfile.readline()

        def log_message(self, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=8814)
    ap.add_argument("--out", default="telemetry")
    ap.add_argument("--keep-content", action="store_true",
                    help="keep content attributes (development with synthetic data only)")
    ap.add_argument("--agent-spans-only", action="store_true",
                    help="keep only the IDs, name, and times of spans that aren't model, tool, "
                         "MCP, or traversal spans (OpenCode exports over a thousand per session)")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(out, args.keep_content, args.agent_spans_only))
    print(f"collector on http://127.0.0.1:{args.port}, writing {out}/", file=sys.stderr, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
