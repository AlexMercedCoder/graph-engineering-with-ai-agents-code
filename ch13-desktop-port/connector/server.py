"""The Chapter 11 governed-data tools as a remote connector, behind OAuth.

    python3 connector/server.py        # serves http://127.0.0.1:8813/mcp

This is what an analyst's Claude Desktop, Cowork, or claude.ai reaches as a
custom connector. Three things differ from the Chapter 11 stdio server:

1. Identity and scopes come from the verified access token, never from the
   environment. Over stdio, whoever launches the server sets CATALOG_IDENTITY,
   and on a desktop that is the person (or the agent) on the laptop. Here the
   only way to be `finance` is to sign in as finance.
2. The token must have been issued for this server (RFC 8707 audience). A token
   minted for any other resource is refused like a missing one.
3. The warehouse, its policies, and the signing key stay on the server. Nothing
   that decides what an analyst may see is installed on the analyst's machine.

The authorization server is authserver.py, mounted on the same origin. It is a
test stand-in for your identity provider, and its load_access_token is also the
connector's token check (known, unexpired, issued for RESOURCE). When your
identity provider replaces it, pass a token_verifier that checks the signature,
issuer, audience, and expiry, and maps the provider's subject to a platform
identity. ISSUER and RESOURCE are hard-coded to 127.0.0.1:8813 for local runs.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH11 = HERE.parent.parent / "ch11-catalog"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CH11 / "server"))
sys.path.insert(0, str(CH11))

import uvicorn  # noqa: E402
import yaml  # noqa: E402
from mcp.server.auth.middleware.auth_context import get_access_token  # noqa: E402
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions  # noqa: E402
from mcp.server.mcpserver import MCPServer  # noqa: E402

import tools  # noqa: E402  (ch11-catalog/server/tools.py)
import validate  # noqa: E402  (ch11-catalog/validate.py)
from authserver import ISSUER, RESOURCE, SCOPES, TestAuthServer, add_consent_routes  # noqa: E402

HOST, PORT = "127.0.0.1", 8813


def token_identity():
    token = get_access_token()
    return token.subject if token and token.subject else "anonymous"


def token_scopes():
    token = get_access_token()
    return set(token.scopes) if token else set()


# The Chapter 11 tools read identity and scopes through these two functions.
# Pointing them at the token is the whole port: the tools, the catalog, the
# validator, and the data platform's policies are unchanged.
tools.current_identity = token_identity
tools.scopes = token_scopes
validate.current_identity = token_identity

provider = TestAuthServer()
mcp = MCPServer(
    "governed-data",
    instructions=("Governed company data: business metrics with their definitions, "
                  "answered under the signed-in person's own data access."),
    auth_server_provider=provider,
    auth=AuthSettings(
        issuer_url=ISSUER,
        resource_server_url=RESOURCE,
        required_scopes=["catalog:read"],
        client_registration_options=ClientRegistrationOptions(
            enabled=True, valid_scopes=SCOPES, default_scopes=SCOPES),
    ),
)


def access_note(identity):
    """One line saying whose access shaped the rows, and which row limits applied.

    It names row filters only. Tables and columns the identity can't see stay
    unnamed, as navigate_catalog leaves them in Chapter 11."""
    policy = yaml.safe_load((CH11 / "warehouse" / "policies.yaml").read_text())["identities"].get(identity) or {}
    limits = [f"{table} rows limited to {rule}" for table, rule in (policy.get("row_filters") or {}).items()]
    return f"Access applied: signed in as {identity}; " + ("; ".join(limits) or "no row limits") + "."


def execute_query(sql: str, max_rows: int = 1000) -> str:
    result = tools.execute_query(sql, max_rows)
    return result if result.startswith(("Forbidden", "Rejected")) else f"{result}\n{access_note(token_identity())}"


# Same description as Chapter 11, plus the line that tells the person whose access applied.
execute_query.__doc__ = tools.execute_query.__doc__ + (
    " Ends with a line saying whose access was applied and which row limits it carries.")

mcp.tool()(tools.navigate_catalog)
mcp.tool()(tools.generate_governed_sql)
mcp.tool()(execute_query)
add_consent_routes(mcp, provider)

METADATA_PATH = "/.well-known/oauth-protected-resource/mcp"
METADATA = json.dumps({"resource": RESOURCE, "authorization_servers": [ISSUER],
                       "scopes_supported": SCOPES, "bearer_methods_supported": ["header"]}).encode()


def advertise_all_scopes(app):
    """Serve protected resource metadata that lists every scope a tool needs.

    The SDK fills scopes_supported from required_scopes, the scope every call
    needs, which here is only catalog:read. Claude requests exactly the scopes
    this document advertises when the 401 names none, so with the SDK's version
    an analyst signs in and can browse definitions but never run a query."""

    async def wrapped(scope, receive, send):
        if scope["type"] == "http" and scope["path"] == METADATA_PATH:
            await send({"type": "http.response.start", "status": 200,
                        "headers": [(b"content-type", b"application/json")]})
            return await send({"type": "http.response.body", "body": METADATA})
        return await app(scope, receive, send)

    return wrapped


app = advertise_all_scopes(mcp.streamable_http_app(json_response=True))

if __name__ == "__main__":
    if not (CH11 / "warehouse" / "warehouse.db").exists():
        raise SystemExit("Run first:  python3 ../ch11-catalog/warehouse/seed.py")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
