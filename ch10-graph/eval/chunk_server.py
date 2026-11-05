#!/usr/bin/env python3
"""The flat retriever behind MCP, for the agent-side benchmark (MCP Python SDK 2.0)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp.server import MCPServer

from chunks import search

mcp = MCPServer("project-docs")


@mcp.tool()
def search_docs(query: str, k: int = 3) -> str:
    """Search the project's architecture documentation and return the k most
    similar sections (default 3, capped at 8). Use for any question about the
    project's services, APIs, databases, and configuration. Returns each
    section with the document and heading it came from."""
    hits = search(query, min(max(k, 1), 8))
    return "\n\n".join(f"[{h['id']}]\n{h['text']}" for h in hits)


if __name__ == "__main__":
    mcp.run()
