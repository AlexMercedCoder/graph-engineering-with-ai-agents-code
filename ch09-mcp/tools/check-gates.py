#!/usr/bin/env python3
"""check-gates.py: the four gate tests from Chapter 9, against a running http_server.py.

    python3 tools/check-gates.py [URL]

Exits 0 only if every gate rejects what it should and passes what it should.
"""
import asyncio
import json
import sys
from pathlib import Path

import httpx2
from mcp.client import Client
from mcp.client.streamable_http import streamable_http_client

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/mcp"
ENV = Path(__file__).resolve().parent.parent / "config" / "test-tokens.env"
TOKENS = dict(line.split("=", 1) for line in ENV.read_text().split())
failures = 0


def check(label, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'pass' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")


async def call(token, tool, args):
    client = httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"})
    async with Client(streamable_http_client(URL, http_client=client)) as c:
        result = await c.call_tool(tool, args)
        return "".join(getattr(part, "text", "") for part in result.content)


def raw(token, tool, args, batch=False):
    """One JSON-RPC POST, to read the HTTP status and challenge directly."""
    headers = {"content-type": "application/json", "accept": "application/json, text/event-stream"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args}}
    r = httpx2.post(URL, headers=headers, content=json.dumps([body] if batch else body))
    return r.status_code, r.headers.get("www-authenticate", "")


async def main():
    status, challenge = raw(None, "lookup_error_code", {"code": "E4021"})
    check("1. no token is refused with 401 and a metadata pointer",
          status == 401 and "resource_metadata=" in challenge, f"{status} {challenge}")

    status, challenge = raw(TOKENS["KB_TOKEN_FOREIGN"], "lookup_error_code", {"code": "E4021"})
    try:
        answered = "Payment authorization expired" in await call(TOKENS["KB_TOKEN_FOREIGN"], "lookup_error_code", {"code": "E4021"})
    except Exception:
        answered = False
    check("2. a token issued for another resource is refused",
          status == 401 and not answered, f"{status}{', and the tool answered it' if answered else ''}")

    status, challenge = raw(TOKENS["KB_TOKEN_ENGINEER"], "get_config_schema", {"service": "payments"})
    check("3. a call outside the token's scope gets 403 naming the scope",
          status == 403 and 'insufficient_scope' in challenge and "schema:read" in challenge, f"{status} {challenge}")

    status, challenge = raw(TOKENS["KB_TOKEN_ENGINEER"], "get_config_schema", {"service": "payments"}, batch=True)
    check("   the same call inside a JSON-RPC batch gets 403 too", status == 403, f"{status}")

    text = await call(TOKENS["KB_TOKEN_OPERATOR"], "get_config_schema", {"service": "payments"})
    check("   the same call with schema:read succeeds", "AUTH_HOLD_MINUTES" in text)

    hidden = await call(TOKENS["KB_TOKEN_ENGINEER"], "find_architecture_docs", {"topic": "fraud scoring"})
    absent = await call(TOKENS["KB_TOKEN_ENGINEER"], "find_architecture_docs", {"topic": "zebra migration"})
    same_shape = hidden.split(". Available")[1:] == absent.split(". Available")[1:]
    check("4. a narrow identity sees no restricted section, shaped like an absent one",
          "0.82" not in hidden and hidden.startswith("No architecture sections") and same_shape)
    wide = await call(TOKENS["KB_TOKEN_SECURITY"], "find_architecture_docs", {"topic": "fraud scoring"})
    check("   the security identity sees it", "0.82" in wide)

    print(f"\n{'all gates hold' if not failures else f'{failures} check(s) failed'}")
    return 1 if failures else 0


raise SystemExit(asyncio.run(main()))
