#!/usr/bin/env python3
"""Print retrieval-worker.md as --agents JSON, with the knowledge server attached to it.

    claude --agents "$(python3 ch12-router/agents/build_agents_json.py)" \
           --strict-mcp-config --mcp-config '{"mcpServers":{}}'

The server is declared inside the worker, so only the worker can see it. In
Claude Code 2.1.316 that works through --agents; an inline mcpServers entry in
the agent file itself didn't start the server in our tests.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent / "knowledge_server.py"
ENV = {"CATALOG_IDENTITY": os.environ.get("CATALOG_IDENTITY", "analyst"),
       "CATALOG_SCOPES": os.environ.get("CATALOG_SCOPES", "catalog:read data:read")}


def definition(python=sys.executable):
    _, front, body = (HERE / "retrieval-worker.md").read_text().split("---", 2)
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", front, re.M))
    return {meta["name"]: {
        "description": meta["description"], "prompt": body.strip(),
        "tools": [t.strip() for t in meta["tools"].split(",")],
        "model": meta["model"], "maxTurns": int(meta["maxTurns"]),
        "mcpServers": [{"project-knowledge": {"command": python, "args": [str(SERVER)], "env": ENV}}]}}


if __name__ == "__main__":
    print(json.dumps(definition()))
