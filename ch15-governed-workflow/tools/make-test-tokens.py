#!/usr/bin/env python3
"""Write the test credentials, readable by you only, valid for eight hours.

  config/test-tokens.json   agent tokens the two servers accept
  config/test-tokens.env    GOVERNED_KNOWLEDGE_TOKEN and GOVERNED_GATE_TOKEN
  config/reviewers.json     reviewer keys and roles for gate/approve.py

The agent gets the tokens and never the reviewer keys. Rerun to replace them.
"""
import json
import os
import secrets
import time
from pathlib import Path

CONFIG = Path(os.environ.get("GOVERNED_CONFIG", Path(__file__).resolve().parent.parent / "config"))
CONFIG.mkdir(exist_ok=True)
exp = int(time.time()) + 8 * 3600
knowledge = "test-" + secrets.token_hex(16)
gate = "test-" + secrets.token_hex(16)
tokens = {
    knowledge: {"client": "agent", "subject": "change-agent", "scopes": ["knowledge:read"],
                "aud": "http://127.0.0.1:8817/mcp", "exp": exp},
    gate: {"client": "agent", "subject": "change-agent", "scopes": ["change:request"],
           "aud": "http://127.0.0.1:8818/mcp", "exp": exp},
}
reviewers = {
    "test-reviewer": {"roles": ["payments-oncall"], "key": secrets.token_hex(32)},
    "dana": {"roles": ["payments-oncall"], "key": secrets.token_hex(32)},
    "sam": {"roles": ["reporting"], "key": secrets.token_hex(32)},
}
files = {
    "test-tokens.json": json.dumps(tokens, indent=1),
    "test-tokens.env": f"GOVERNED_KNOWLEDGE_TOKEN={knowledge}\nGOVERNED_GATE_TOKEN={gate}\n",
    "reviewers.json": json.dumps(reviewers, indent=1),
}
for name, text in files.items():
    path = CONFIG / name
    path.touch(mode=0o600)
    os.chmod(path, 0o600)
    path.write_text(text)
print(f"wrote {', '.join(files)} in {CONFIG}")
