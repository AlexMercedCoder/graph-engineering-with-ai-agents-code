"""A test OAuth 2.1 authorization server for the governed-data connector.

It implements the MCP SDK's OAuthAuthorizationServerProvider, so the SDK serves
the standard endpoints (/.well-known/oauth-authorization-server, /register,
/authorize, /token) and this file decides who gets which token. In production
your identity provider does this job; keep the resource and scope rules.

What it enforces, because the connector's security depends on each one:
- Dynamic Client Registration, so Claude can register itself ("Register
  automatically" in the Add custom connector dialog).
- PKCE with S256 on every authorization (the SDK checks the verifier).
- Resource binding (RFC 8707): a token carries the resource it was issued for,
  and the connector accepts only its own. This server also issues tokens for a
  second application, OTHER_RESOURCE, so you can watch the connector refuse one.
- Scopes come from the user's role, not from what the client asks for.
- Refresh tokens rotate; a used refresh token answers invalid_grant.

The consent page stands in for single sign-on. It lists the test users; picking
one is the sign-in. Never put a page like this in front of real data.
"""
import html
import secrets
import time

from mcp.server.auth.provider import (AccessToken, AuthorizationCode, AuthorizeError, RefreshToken,
                                      construct_redirect_uri)
from mcp.shared.auth import OAuthToken
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

ISSUER = "http://127.0.0.1:8813"
RESOURCE = "http://127.0.0.1:8813/mcp"
OTHER_RESOURCE = "http://127.0.0.1:8813/reports"
SCOPES = ["catalog:read", "data:read"]
ACCESS_TTL, REFRESH_TTL = 3600, 30 * 86400

# Test sign-ins: the identity the data platform sees, and the most scope each may hold.
USERS = {
    "analyst": ("analyst", ["catalog:read", "data:read"]),
    "emea-analyst": ("emea-analyst", ["catalog:read", "data:read"]),
    "finance": ("finance", ["catalog:read", "data:read"]),
    "new-analyst": ("analyst", ["catalog:read"]),  # onboarding: browse definitions, read no rows
}


class TestAuthServer:
    def __init__(self):
        self.clients, self.pending, self.codes = {}, {}, {}
        self.access, self.refresh = {}, {}

    # Client registration (DCR, RFC 7591)
    async def get_client(self, client_id):
        return self.clients.get(client_id)

    async def register_client(self, client_info):
        self.clients[client_info.client_id] = client_info

    # Authorization: park the request and send the browser to the consent page
    async def authorize(self, client, params):
        if params.resource not in (None, RESOURCE, OTHER_RESOURCE):
            raise AuthorizeError("invalid_target", f"unknown resource {params.resource}")
        request_id = secrets.token_urlsafe(16)
        self.pending[request_id] = (client.client_id, params)
        return f"{ISSUER}/consent?request={request_id}"

    def approve(self, request_id, user):
        client_id, params = self.pending.pop(request_id)
        wanted = params.scopes or SCOPES
        code = AuthorizationCode(
            code=secrets.token_urlsafe(32), client_id=client_id, subject=USERS[user][0],
            scopes=[s for s in wanted if s in USERS[user][1]],
            expires_at=time.time() + 300, code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource or RESOURCE)
        self.codes[code.code] = code
        return construct_redirect_uri(str(params.redirect_uri), code=code.code, state=params.state)

    async def load_authorization_code(self, client, authorization_code):
        code = self.codes.get(authorization_code)
        return code if code and code.client_id == client.client_id else None

    async def exchange_authorization_code(self, client, authorization_code):
        del self.codes[authorization_code.code]
        return self._issue(client.client_id, authorization_code.subject,
                           authorization_code.scopes, authorization_code.resource)

    # Refresh, with rotation: the old refresh token stops working
    async def load_refresh_token(self, client, refresh_token):
        entry = self.refresh.get(refresh_token)
        return entry[0] if entry and entry[0].client_id == client.client_id else None

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        _, resource = self.refresh.pop(refresh_token.token)
        return self._issue(client.client_id, refresh_token.subject, scopes, resource)

    # The connector's token check: known, unexpired, and issued for this server
    async def load_access_token(self, token):
        entry = self.access.get(token)
        if entry is None or entry.expires_at < time.time() or entry.resource != RESOURCE:
            return None
        return entry

    async def revoke_token(self, token):
        self.access.pop(token.token, None)
        self.refresh.pop(token.token, None)

    def _issue(self, client_id, subject, scopes, resource):
        now = int(time.time())
        access = AccessToken(token=secrets.token_urlsafe(32), client_id=client_id, scopes=scopes,
                             expires_at=now + ACCESS_TTL, resource=resource, subject=subject)
        refresh = RefreshToken(token=secrets.token_urlsafe(32), client_id=client_id, scopes=scopes,
                               expires_at=now + REFRESH_TTL, subject=subject)
        self.access[access.token] = access
        self.refresh[refresh.token] = (refresh, resource)
        return OAuthToken(access_token=access.token, token_type="Bearer", expires_in=ACCESS_TTL,
                          refresh_token=refresh.token, scope=" ".join(scopes))


def add_consent_routes(mcp, provider):
    """The sign-in page. A real deployment redirects to your identity provider."""

    @mcp.custom_route("/consent", methods=["GET"])
    async def consent(request: Request) -> Response:
        rid = request.query_params.get("request", "")
        if rid not in provider.pending:
            return HTMLResponse("Unknown or expired sign-in request.", status_code=400)
        client_id, params = provider.pending[rid]
        client = provider.clients[client_id]
        links = "".join(
            f'<li><a href="/consent/approve?request={rid}&user={u}">Sign in as {u}</a> '
            f'({", ".join(s)})</li>' for u, (_, s) in USERS.items())
        return HTMLResponse(
            f"<h1>governed-data test sign-in</h1>"
            f"<p>{html.escape(client.client_name or client_id)} asks for access to "
            f"{html.escape(params.resource or RESOURCE)}, returning you to "
            f"<b>{html.escape(str(params.redirect_uri))}</b>.</p><ul>{links}</ul>")

    @mcp.custom_route("/consent/approve", methods=["GET"])
    async def approve(request: Request) -> Response:
        rid, user = request.query_params.get("request", ""), request.query_params.get("user", "")
        if rid not in provider.pending or user not in USERS:
            return HTMLResponse("Unknown request or user.", status_code=400)
        return RedirectResponse(provider.approve(rid, user), status_code=302)
