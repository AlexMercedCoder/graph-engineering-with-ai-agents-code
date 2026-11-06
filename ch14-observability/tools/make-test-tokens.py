#!/usr/bin/env python3
"""Write config/test-tokens.json and config/test-tokens.env: three random test
tokens for the local graph server, valid for eight hours.

  sre         graph:read config:read    subject sre-oncall
  contractor  graph:read                subject contractor-7
  foreign     graph:read config:read    issued for another resource

The files are gitignored; rerun this script to replace the tokens.
"""
import json
import secrets
import time
from pathlib import Path

RESOURCE = "http://127.0.0.1:8815/mcp"
OTHER = "https://billing.example.com/mcp"
out = Path(__file__).resolve().parent.parent / "config" / "test-tokens.json"
out.parent.mkdir(exist_ok=True)
table, names = {}, {}
for name, scopes, subject, aud in [
    ("sre", ["graph:read", "config:read"], "sre-oncall", RESOURCE),
    ("contractor", ["graph:read"], "contractor-7", RESOURCE),
    ("foreign", ["graph:read", "config:read"], "sre-oncall", OTHER),
]:
    token = "test-" + secrets.token_hex(16)
    table[token] = {"client": name, "scopes": scopes, "subject": subject, "aud": aud,
                    "exp": int(time.time()) + 8 * 3600}
    names[name] = token
out.write_text(json.dumps(table, indent=1))
(out.parent / "test-tokens.env").write_text(
    "".join(f"GRAPH_TOKEN_{n.upper()}={t}\n" for n, t in names.items()))
print(f"wrote {out} and test-tokens.env")
