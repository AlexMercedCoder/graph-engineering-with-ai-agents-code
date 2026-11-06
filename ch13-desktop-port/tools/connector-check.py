#!/usr/bin/env python3
"""connector-check.py: sign in to the connector the way Claude's hosted apps do.

    python3 tools/connector-check.py [URL]            # every check; exit 0 if all pass
    python3 tools/connector-check.py --token analyst  # sign in and print an access token

Claude's connector client (claude.ai, Desktop, mobile, and Cowork share it) has
documented requirements beyond the MCP specification: a 401 carrying a
resource_metadata pointer, a metadata `resource` equal to the URL the user types,
the first authorization server only, S256 PKCE, and the redirect URI
https://claude.ai/api/mcp/auth_callback. This script follows that path with the
test authorization server's consent page standing in for the browser, then
checks what each identity can do once signed in.

It does not prove Claude itself can connect: Claude reaches a custom connector
from Anthropic's servers, so the server must be on a public HTTPS address (or
behind an MCP tunnel), and someone has to sign in from the app.
"""
import asyncio
import base64
import hashlib
import secrets
import sys
from urllib.parse import parse_qs, urlparse

import httpx2
from mcp.client import Client
from mcp.client.streamable_http import streamable_http_client

args = [a for a in sys.argv[1:] if not a.startswith("--")]
URL = args[0] if args and "://" in args[0] else "http://127.0.0.1:8813/mcp"
CALLBACK = "https://claude.ai/api/mcp/auth_callback"
failures = 0


def check(label, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'pass' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    return ok


def line(text, n=-1):
    """The nth line of a tool result, for the detail column."""
    lines = text.splitlines() or [""]
    return lines[max(n, -len(lines))]


def discover(http):
    r = http.post(URL, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                  headers={"accept": "application/json, text/event-stream"})
    challenge = r.headers.get("www-authenticate", "")
    pointer = challenge.split('resource_metadata="')[1].split('"')[0] if "resource_metadata=" in challenge else ""
    prm = http.get(pointer).json() if pointer else {}
    issuer = (prm.get("authorization_servers") or [""])[0]
    asm = http.get(issuer.rstrip("/") + "/.well-known/oauth-authorization-server").json() if issuer else {}
    return r, pointer, prm, asm


def sign_in(http, asm, scopes, user, resource=URL, register=None):
    """DCR, then an authorization code with PKCE, approved as `user` on the consent page."""
    client = register or http.post(asm["registration_endpoint"], json={
        "client_name": "Claude", "redirect_uris": [CALLBACK], "token_endpoint_auth_method": "none",
        "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"]}).json()
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(16)
    r = http.get(asm["authorization_endpoint"], params={
        "response_type": "code", "client_id": client["client_id"], "redirect_uri": CALLBACK,
        "code_challenge": challenge, "code_challenge_method": "S256", "state": state,
        "scope": " ".join(scopes), "resource": resource})
    consent = r.headers["location"]
    request_id = parse_qs(urlparse(consent).query)["request"][0]
    r = http.get(f"{urlparse(consent).scheme}://{urlparse(consent).netloc}/consent/approve",
                 params={"request": request_id, "user": user})
    back = parse_qs(urlparse(r.headers["location"]).query)
    assert back["state"][0] == state, "state changed on the way back"
    tokens = http.post(asm["token_endpoint"], data={
        "grant_type": "authorization_code", "code": back["code"][0], "redirect_uri": CALLBACK,
        "client_id": client["client_id"], "code_verifier": verifier, "resource": resource}).json()
    return client, tokens


async def call(token, tool, arguments):
    http = httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"})
    async with Client(streamable_http_client(URL, http_client=http)) as c:
        result = await c.call_tool(tool, arguments)
        return "".join(getattr(p, "text", "") for p in result.content)


def ask(token, metric, dims, period, filters=None):
    sql = asyncio.run(call(token, "generate_governed_sql",
                           {"metric": metric, "dimensions": dims, "time_range": period, "filters": filters}))
    return sql, asyncio.run(call(token, "execute_query", {"sql": sql}))


def main():
    http = httpx2.Client(follow_redirects=False, timeout=10)
    r, pointer, prm, asm = discover(http)

    if "--token" in sys.argv:
        user = args[0] if args and "://" not in args[0] else "analyst"
        _, tokens = sign_in(http, asm, prm["scopes_supported"], user)
        print(tokens["access_token"])
        return

    print("Discovery, as Claude's connector client performs it")
    check("unauthenticated call answers 401", r.status_code == 401, str(r.status_code))
    check("401 carries a resource_metadata pointer", bool(pointer), pointer)
    check("metadata resource equals the URL users enter", prm.get("resource") == URL, prm.get("resource", ""))
    check("first authorization server serves RFC 8414 metadata", "token_endpoint" in asm)
    check("S256 PKCE advertised", "S256" in asm.get("code_challenge_methods_supported", []))
    cimd = asm.get("client_id_metadata_document_supported") and \
        "none" in asm.get("token_endpoint_auth_methods_supported", [])
    check("client registration available (DCR or CIMD)", bool(asm.get("registration_endpoint") or cimd),
          "CIMD" if cimd else "DCR: Claude uses 'Register automatically'")
    needed = {"catalog:read", "data:read"}
    check("metadata advertises every scope the tools need", needed <= set(prm.get("scopes_supported", [])),
          " ".join(prm.get("scopes_supported", [])))

    print("\nSign-in as analyst, redirect to " + CALLBACK)
    client, tokens = sign_in(http, asm, prm.get("scopes_supported", []), "analyst")
    check("authorization code exchanged for tokens", "access_token" in tokens, tokens.get("error", ""))
    check("token carries the analyst's scopes", set(tokens.get("scope", "").split()) == needed, tokens.get("scope", ""))
    analyst = tokens["access_token"]

    print("\nWhat each signed-in identity gets")
    sql, rows = ask(analyst, "net_written_premium", ["region"], "2026-Q3")
    check("analyst: net written premium by region runs", "rows)" in rows and "identity analyst" in sql,
          line(rows, -2))
    check("analyst: the result names no table the analyst can't see", "commission" not in rows, line(rows, -1))
    cat = asyncio.run(call(analyst, "navigate_catalog", {"concept": "commission"}))
    check("analyst: commission is not in the catalog the analyst sees", "commission_paid (" not in cat)
    _, emea = sign_in(http, asm, prm["scopes_supported"], "emea-analyst")
    _, rows = ask(emea["access_token"], "net_written_premium", ["region"], "2026-Q3")
    check("emea-analyst: the same query returns EMEA only", "(1 row)" in rows, line(rows, -2))
    check("emea-analyst: the result names the row policy that applied", "rows limited to" in rows,
          line(rows, -1)[:70])
    _, new = sign_in(http, asm, prm["scopes_supported"], "new-analyst")
    sql2 = asyncio.run(call(new["access_token"], "generate_governed_sql",
                            {"metric": "net_written_premium", "dimensions": ["region"], "time_range": "2026-Q3"}))
    out = asyncio.run(call(new["access_token"], "execute_query", {"sql": sql2}))
    check("new-analyst: SQL generates, execution is refused", "-- governed:" in sql2 and out.startswith("Forbidden"),
          line(out, 0))
    out = asyncio.run(call(emea["access_token"], "execute_query", {"sql": sql}))
    check("SQL signed for analyst won't run under another identity", out.startswith("Rejected"), out[:60])

    print("\nToken handling")
    _, other = sign_in(http, asm, prm["scopes_supported"], "finance", resource=URL.rsplit("/", 1)[0] + "/reports")
    r = http.post(URL, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                  headers={"authorization": f"Bearer {other['access_token']}",
                           "accept": "application/json, text/event-stream"})
    check("finance token issued for another application is refused", r.status_code == 401, str(r.status_code))
    fresh = http.post(asm["token_endpoint"], data={"grant_type": "refresh_token", "client_id": client["client_id"],
                                                    "refresh_token": tokens["refresh_token"]}).json()
    check("refresh returns a new access and refresh token",
          fresh.get("refresh_token") not in (None, tokens["refresh_token"]))
    again = http.post(asm["token_endpoint"], data={"grant_type": "refresh_token", "client_id": client["client_id"],
                                                    "refresh_token": tokens["refresh_token"]})
    check("a used refresh token answers invalid_grant", again.json().get("error") == "invalid_grant",
          again.json().get("error", ""))

    print("\nall checks pass" if failures == 0 else f"\n{failures} check(s) failed")
    sys.exit(failures != 0)


if __name__ == "__main__":
    main()
