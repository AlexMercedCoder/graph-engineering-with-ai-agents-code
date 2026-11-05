#!/usr/bin/env python3
"""Write config/test-tokens.json: four random test tokens for the local HTTP server,
valid for eight hours.

Each token is opaque and works only against http_server.py on 127.0.0.1. The
file is gitignored; rerun this script to replace the tokens.

  engineer   knowledge:read                 subject engineer
  operator   knowledge:read schema:read     subject engineer
  security   knowledge:read schema:read     subject security
  foreign    knowledge:read schema:read     issued for another resource
"""
import json
import secrets
import time
from pathlib import Path

RESOURCE = "http://127.0.0.1:8765/mcp"
OTHER = "https://billing.example.com/mcp"
out = Path(__file__).resolve().parent.parent / "config" / "test-tokens.json"
table, names = {}, {}
for name, scopes, subject, aud in [
    ("engineer", ["knowledge:read"], "engineer", RESOURCE),
    ("operator", ["knowledge:read", "schema:read"], "engineer", RESOURCE),
    ("security", ["knowledge:read", "schema:read"], "security", RESOURCE),
    ("foreign", ["knowledge:read", "schema:read"], "engineer", OTHER),
]:
    token = "test-" + secrets.token_hex(16)
    table[token] = {"client": name, "scopes": scopes, "subject": subject, "aud": aud,
                    "exp": int(time.time()) + 8 * 3600}
    names[name] = token
out.write_text(json.dumps(table, indent=1))
(out.parent / "test-tokens.env").write_text("".join(f"KB_TOKEN_{n.upper()}={t}\n" for n, t in names.items()))
print(f"wrote {out} and test-tokens.env")
