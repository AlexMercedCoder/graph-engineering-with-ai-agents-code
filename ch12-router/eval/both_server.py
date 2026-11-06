#!/usr/bin/env python3
"""Chapter 10's vector search and graph traversal tools in one MCP server.

The "free choice" setup of run_routed.py: the agent sees all four tools and
picks for itself, with no router in front.
"""
import sys
from pathlib import Path

CH10 = Path(__file__).resolve().parents[2] / "ch10-graph"
sys.path[:0] = [str(CH10 / "eval"), str(CH10 / "graph")]
from mcp.server import MCPServer  # noqa: E402

from chunk_server import search_docs  # noqa: E402
from traversal import find_dependencies, find_dependents, trace_configuration  # noqa: E402

mcp = MCPServer("project-docs-and-graph")
for tool in (search_docs, find_dependents, find_dependencies, trace_configuration):
    mcp.tool()(tool)

if __name__ == "__main__":
    mcp.run()
