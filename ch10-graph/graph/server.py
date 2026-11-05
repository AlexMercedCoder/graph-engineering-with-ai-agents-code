#!/usr/bin/env python3
"""The Chapter 10 traversal tools behind MCP (MCP Python SDK 2.0).

    python3 server.py        runs over stdio; register it with your harness
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp.server import MCPServer

from traversal import find_dependencies, find_dependents, trace_configuration

mcp = MCPServer("project-graph")
mcp.tool()(find_dependents)
mcp.tool()(find_dependencies)
mcp.tool()(trace_configuration)

if __name__ == "__main__":
    mcp.run()
