"""The Chapter 9 server over Streamable HTTP, behind the three gates.

    python3 ../tools/make-test-tokens.py     # writes ../config/test-tokens.json
    python3 http_server.py                   # serves http://127.0.0.1:8765/mcp

Gate one, authentication: a bearer token must be one this server issued for
this resource. A token for any other audience is refused like a missing one.
Gate two, authorization: every call needs knowledge:read, and get_config_schema
also needs schema:read. A missing scope is a 403 naming it.
Gate three, data scoping: find_architecture_docs filters by the token's
subject, inside the tool (see tools.py and knowledge.py).

The token table stands in for an OAuth 2.1 authorization server. In production,
verify_token validates a JWT or calls the issuer's introspection endpoint; the
audience check and the scope checks stay the same.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import find_architecture_docs, get_config_schema, lookup_error_code

import uvicorn
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings

HOST, PORT = "127.0.0.1", 8765
RESOURCE = f"http://{HOST}:{PORT}/mcp"
ISSUER = "http://127.0.0.1:8766"
METADATA = f"http://{HOST}:{PORT}/.well-known/oauth-protected-resource/mcp"
TOKENS = Path(__file__).resolve().parent.parent / "config" / "test-tokens.json"

# Scopes each tool needs beyond knowledge:read.
TOOL_SCOPES = {"get_config_schema": ["schema:read"]}


class TableVerifier:
    """Accepts a token only if it was issued for this server (RFC 8707 audience)."""

    def __init__(self, path):
        self.table = json.loads(path.read_text())

    async def verify_token(self, token):
        entry = self.table.get(token)
        if entry is None or entry["aud"] != RESOURCE:
            return None
        return AccessToken(token=token, client_id=entry["client"], scopes=entry["scopes"],
                           resource=entry["aud"], subject=entry["subject"], expires_at=entry["exp"])


verifier = TableVerifier(TOKENS)
mcp = MCPServer(
    "project-knowledge",
    token_verifier=verifier,
    auth=AuthSettings(issuer_url=ISSUER, resource_server_url=RESOURCE,
                      required_scopes=["knowledge:read"]),
)
mcp.tool()(lookup_error_code)
mcp.tool()(get_config_schema)
mcp.tool()(find_architecture_docs)


def per_tool_scopes(app):
    """Return 403 insufficient_scope before a tools/call reaches a tool whose
    scope the token lacks, naming every scope the call needs in one challenge."""

    async def wrapped(scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST":
            return await app(scope, receive, send)
        chunks, more = [], True
        while more:
            message = await receive()
            chunks.append(message.get("body", b""))
            more = message.get("more_body", False)
        body = b"".join(chunks)

        replayed = False

        async def replay():
            nonlocal replayed
            if replayed:
                return await receive()
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}

        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = {}
        messages = parsed if isinstance(parsed, list) else [parsed]
        needed = sorted({scope for m in messages if isinstance(m, dict) and m.get("method") == "tools/call"
                         for scope in TOOL_SCOPES.get((m.get("params") or {}).get("name"), [])})
        header = dict(scope["headers"]).get(b"authorization", b"").decode()
        token = await verifier.verify_token(header[7:]) if header.lower().startswith("bearer ") else None
        if needed and token is not None:
            missing = [s for s in ["knowledge:read", *needed] if s not in token.scopes]
            if missing:
                challenge = (f'Bearer error="insufficient_scope", scope="{" ".join(["knowledge:read", *needed])}", '
                             f'resource_metadata="{METADATA}"')
                payload = json.dumps({"error": "insufficient_scope", "scope": " ".join(missing)}).encode()
                await send({"type": "http.response.start", "status": 403,
                            "headers": [(b"content-type", b"application/json"),
                                        (b"www-authenticate", challenge.encode())]})
                return await send({"type": "http.response.body", "body": payload})
        return await app(scope, replay, send)

    return wrapped


app = per_tool_scopes(mcp.streamable_http_app(json_response=True))

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
