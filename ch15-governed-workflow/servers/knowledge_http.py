#!/usr/bin/env python3
"""Chapter 12's project-knowledge server over Streamable HTTP, behind a token.

    python3 knowledge_http.py          serves http://127.0.0.1:8817/mcp

The tools are Chapter 12's functions, imported rather than copied, so the
router, the evidence envelopes, and the Chapter 9 to 11 paths behave exactly
as they did there. The governed-data tools read CATALOG_IDENTITY and
CATALOG_SCOPES from this process's environment, as in Chapter 11.
"""
import os

from common import COLLECTOR, auth, serve, tracer

PORT = int(os.environ.get("KNOWLEDGE_PORT", 8817))
RESOURCE = f"http://127.0.0.1:{PORT}/mcp"
TOOLS = ["route_question", "check_evidence", "lookup_error_code", "get_config_schema",
         "search_docs", "find_dependents", "find_dependencies", "trace_configuration",
         "navigate_catalog", "generate_governed_sql", "execute_query"]

tracer("project-knowledge")
os.environ.setdefault("CATALOG_IDENTITY", "analyst")
os.environ.setdefault("CATALOG_SCOPES", "catalog:read data:read")
import knowledge_server  # noqa: E402  (Chapter 12)
from mcp.server import MCPServer  # noqa: E402

mcp = MCPServer("project-knowledge", **auth(RESOURCE, ["knowledge:read"]))
for name in TOOLS:
    mcp.tool(name=name)(getattr(knowledge_server, name))

if __name__ == "__main__":
    print(f"project-knowledge on {RESOURCE} (spans to {COLLECTOR or 'nowhere'})", flush=True)
    serve(mcp, PORT)
