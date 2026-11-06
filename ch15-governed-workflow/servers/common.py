"""What both Chapter 15 servers share: paths, test-token checks, and tracing.

The servers bind to 127.0.0.1 and accept the bearer tokens that
tools/make-test-tokens.py writes. In production, put them behind the
OAuth connector from Chapter 13 instead, so identity comes from a token
your identity provider signed.
"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH15 = HERE.parent
ROOT = CH15.parent
STATE = Path(os.environ.get("GOVERNED_STATE", CH15 / "state"))
CONFIG = Path(os.environ.get("GOVERNED_CONFIG", CH15 / "config"))
TOKENS = CONFIG / "test-tokens.json"
COLLECTOR = os.environ.get("COLLECTOR")          # e.g. http://127.0.0.1:8819; unset means no spans

sys.path[:0] = [str(ROOT / "ch12-router"), str(ROOT / "ch10-graph" / "graph"),
                str(ROOT / "ch09-mcp" / "server")]


def tracer(service):
    """A tracer that exports to COLLECTOR, or a no-op one when COLLECTOR is unset."""
    from opentelemetry import trace
    if COLLECTOR:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        provider = TracerProvider(resource=Resource.create({"service.name": service}))
        provider.add_span_processor(BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{COLLECTOR}/v1/traces"), schedule_delay_millis=1000))
        trace.set_tracer_provider(provider)
    return trace.get_tracer(service)


class TokenTable:
    """Accepts a test token only for the resource it was issued for, before it expires."""

    def __init__(self, resource):
        self.resource = resource

    async def verify_token(self, token):
        from mcp.server.auth.provider import AccessToken
        entry = json.loads(TOKENS.read_text()).get(token)
        if entry is None or entry["aud"] != self.resource or entry["exp"] < time.time():
            return None
        return AccessToken(token=token, client_id=entry["client"], scopes=entry["scopes"],
                           resource=entry["aud"], subject=entry["subject"], expires_at=entry["exp"])


def auth(resource, scopes):
    from mcp.server.auth.settings import AuthSettings
    return dict(token_verifier=TokenTable(resource),
                auth=AuthSettings(issuer_url="http://127.0.0.1:8816", resource_server_url=resource,
                                  validate_token_resource=True, required_scopes=scopes))


def header_context_to_meta(app):
    """Chapter 14's adapter: Claude Code sends W3C trace context as an HTTP
    traceparent header, and the MCP SDK reads it from params._meta. Copy the
    header into _meta when the message doesn't carry one."""

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
            if isinstance(msg, dict) and msg.get("method") == "tools/call" and "traceparent" in headers:
                meta = msg.setdefault("params", {}).setdefault("_meta", {})
                meta.setdefault("traceparent", headers["traceparent"])
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


def serve(mcp, port):
    import uvicorn
    uvicorn.run(header_context_to_meta(mcp.streamable_http_app()), host="127.0.0.1", port=port,
                log_level="warning")
