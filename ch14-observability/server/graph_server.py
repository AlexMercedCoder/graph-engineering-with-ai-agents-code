#!/usr/bin/env python3
"""The Chapter 10 graph tools over Streamable HTTP, traced and behind two scopes.

    python3 ../tools/make-test-tokens.py      # writes ../config/test-tokens.json
    python3 graph_server.py                   # serves http://127.0.0.1:8815/mcp

Spans go to the collector on http://127.0.0.1:8814. The MCP Python SDK 2.x
already emits one SERVER span per message (`tools/call find_dependents`); this
file adds one child span per tool with the attributes the conventions don't
cover: how deep the traversal was asked to go, how deep it got, how many paths
it found, whether one more hop would have found more, and who asked.

Scopes: every tool needs graph:read; trace_configuration also needs
config:read, because configuration keys include secrets' names and owners.

When one more hop would have found more services, find_dependents says so in
its reply, so the agent can tell the user (GRAPH_REPORT_COVERAGE=0 turns this
off, as the server was before the chapter's runs exposed the gap).

Fault switch, for the regression exercise:
  GRAPH_MAX_DEPTH=1        a configuration change that lowers the depth cap
"""
import json
import os
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "ch10-graph" / "graph"))
import traversal  # noqa: E402
from traversal import resolve_entity, traverse_incoming  # noqa: E402

import uvicorn  # noqa: E402
from mcp.server import MCPServer  # noqa: E402
from mcp.server.auth.middleware.auth_context import get_access_token  # noqa: E402
from mcp.server.auth.provider import AccessToken  # noqa: E402
from mcp.server.auth.settings import AuthSettings  # noqa: E402
from opentelemetry import trace  # noqa: E402
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # noqa: E402
from opentelemetry.sdk.resources import Resource  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: E402

HOST, PORT = "127.0.0.1", int(os.environ.get("GRAPH_PORT", 8815))
RESOURCE = "http://127.0.0.1:8815/mcp"      # the audience the test tokens are issued for
COLLECTOR = os.environ.get("COLLECTOR", "http://127.0.0.1:8814")
TOKENS = HERE.parent / "config" / "test-tokens.json"
AUDIT_LOG = os.environ.get("GRAPH_AUDIT_LOG")      # a JSON-lines record for harnesses without tracing
traversal.MAX_DEPTH = int(os.environ.get("GRAPH_MAX_DEPTH", traversal.MAX_DEPTH))
REPORT_COVERAGE = os.environ.get("GRAPH_REPORT_COVERAGE", "1") == "1"

provider = TracerProvider(resource=Resource.create({"service.name": "project-graph"}))
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint=f"{COLLECTOR}/v1/traces"), schedule_delay_millis=1000))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("project-graph")


class TableVerifier:
    def __init__(self, path):
        self.table = json.loads(path.read_text())

    async def verify_token(self, token):
        entry = self.table.get(token)
        if entry is None or entry["aud"] != RESOURCE:
            return None
        return AccessToken(token=token, client_id=entry["client"], scopes=entry["scopes"],
                           resource=entry["aud"], subject=entry["subject"], expires_at=entry["exp"])


def who():
    tok = get_access_token()
    return (tok.subject if tok else None), set(tok.scopes if tok else [])


_probe_lock = threading.Lock()


def one_hop_further(root, depth):
    """Walk one hop past the cap. traverse_incoming clamps to MAX_DEPTH itself, so
    a probe through it can never see past the cap and would call every capped
    walk complete; lift the cap for this one call."""
    with _probe_lock:
        cap, traversal.MAX_DEPTH = traversal.MAX_DEPTH, depth + 1
        try:
            return traverse_incoming(root, ["CALLS", "DEPENDS_ON"], depth + 1)
        finally:
            traversal.MAX_DEPTH = cap


def audit(span, tool):
    """Append the span's attributes as one JSON line, when GRAPH_AUDIT_LOG is set."""
    if AUDIT_LOG:
        with open(AUDIT_LOG, "a") as f:
            record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tool": tool,
                      **{k: list(v) if isinstance(v, tuple) else v for k, v in span.attributes.items()}}
            f.write(json.dumps(record) + "\n")


def traced_dependents(service_or_endpoint: str, max_depth: int = 2) -> str:
    with tracer.start_as_current_span("graph.find_dependents") as span:
        subject, scopes = who()
        span.set_attributes({"graph.subject": subject or "unknown", "graph.depth_requested": max_depth,
                             "graph.depth_cap": traversal.MAX_DEPTH})
        depth = min(max(max_depth, 1), traversal.MAX_DEPTH)
        try:
            root, _, _ = resolve_entity(service_or_endpoint, ("Service", "APIEndpoint"))
        except traversal.GraphMissing:
            root = None
        if root is None:
            span.set_attributes({"graph.paths_found": 0, "error.type": "entity_not_found"})
            return traversal.find_dependents(service_or_endpoint, max_depth)
        paths = traverse_incoming(root, ["CALLS", "DEPENDS_ON"], depth)
        beyond = one_hop_further(root, depth)
        span.set_attributes({
            "graph.root": root.name,
            "graph.depth_used": depth,
            "graph.depth_reached": max((len(p.hops) for p in paths), default=0),
            "graph.paths_found": len(paths),
            "graph.coverage": "partial" if len(beyond) > len(paths) else "complete",
            "graph.targets": sorted({p.target.name for p in paths}),
        })
        audit(span, "find_dependents")
        reply = traversal.find_dependents(service_or_endpoint, max_depth)
        if REPORT_COVERAGE and len(beyond) > len(paths):
            reply += (f"\nCoverage is partial: more services depend on {root.name} beyond "
                      f"{depth} hop{'' if depth == 1 else 's'}, and this server's depth cap "
                      f"is {traversal.MAX_DEPTH}.")
        return reply


def traced_dependencies(service: str, max_depth: int = 2) -> str:
    with tracer.start_as_current_span("graph.find_dependencies") as span:
        subject, _ = who()
        span.set_attributes({"graph.subject": subject or "unknown", "graph.depth_requested": max_depth})
        return traversal.find_dependencies(service, max_depth)


def traced_configuration(key_or_service: str) -> str:
    with tracer.start_as_current_span("graph.trace_configuration") as span:
        subject, scopes = who()
        span.set_attributes({"graph.subject": subject or "unknown", "auth.scope_required": "config:read"})
        if "config:read" not in scopes:
            span.set_attributes({"auth.decision": "deny", "error.type": "insufficient_scope"})
            span.set_status(trace.StatusCode.ERROR, "insufficient_scope")
            audit(span, "trace_configuration")
            raise PermissionError("trace_configuration needs the config:read scope, which this "
                                  "token doesn't carry. Ask the platform team for access.")
        span.set_attribute("auth.decision", "allow")
        audit(span, "trace_configuration")
        return traversal.trace_configuration(key_or_service)


for fn, original in ((traced_dependents, traversal.find_dependents),
                     (traced_dependencies, traversal.find_dependencies),
                     (traced_configuration, traversal.trace_configuration)):
    fn.__doc__ = original.__doc__

mcp = MCPServer(
    "project-graph",
    token_verifier=TableVerifier(TOKENS),
    auth=AuthSettings(issuer_url="http://127.0.0.1:8816", resource_server_url=RESOURCE,
                      validate_token_resource=True,
                      required_scopes=["graph:read"]),
)
mcp.tool(name="find_dependents")(traced_dependents)
mcp.tool(name="find_dependencies")(traced_dependencies)
mcp.tool(name="trace_configuration")(traced_configuration)


def header_context_to_meta(app):
    """Claude Code sends W3C trace context as an HTTP traceparent header. The SDK
    reads it from params._meta, where the MCP conventions put it. Copy the header
    into _meta when the message doesn't already carry one."""

    async def wrapped(scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST":
            return await app(scope, receive, send)
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        chunks, more = [], True
        while more:
            message = await receive()
            chunks.append(message.get("body", b""))
            more = message.get("more_body", False)
        body = b"".join(chunks)
        try:
            msg = json.loads(body)
            if isinstance(msg, dict) and msg.get("method") == "tools/call":
                meta = msg.setdefault("params", {}).setdefault("_meta", {})
                source = "meta" if "traceparent" in meta else "none"
                if source == "none" and "traceparent" in headers:
                    meta["traceparent"] = headers["traceparent"]
                    source = "header"
                print(f"tools/call {msg['params'].get('name')}: trace context from {source}",
                      file=sys.stderr, flush=True)
                body = json.dumps(msg).encode()
        except ValueError:
            pass
        replayed = False

        async def replay():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        new_headers = [(k, v) for k, v in scope["headers"] if k.lower() != b"content-length"]
        new_headers.append((b"content-length", str(len(body)).encode()))
        return await app(dict(scope, headers=new_headers), replay, send)

    return wrapped


if __name__ == "__main__":
    if not TOKENS.exists():
        raise SystemExit("No test tokens yet. Run: python3 ../tools/make-test-tokens.py")
    print(f"project-graph on {RESOURCE} (depth cap {traversal.MAX_DEPTH}, spans to {COLLECTOR})",
          file=sys.stderr, flush=True)
    uvicorn.run(header_context_to_meta(mcp.streamable_http_app()), host=HOST, port=PORT,
                log_level="warning")
