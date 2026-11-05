"""The Chapter 9 MCP server over stdio. Requires the MCP Python SDK 2.x:

    pip install "mcp>=2,<3"
    python3 server.py

The tool bodies live in tools.py so that cli.py can expose the same operations
without the SDK. The docstrings become the routing descriptions, which is why
they follow the four-part template from Chapter 4.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import find_architecture_docs, get_config_schema, lookup_error_code

try:
    from mcp.server import MCPServer
except ImportError:  # pragma: no cover
    raise SystemExit(
        "The MCP SDK 2.x is not installed. Either run:\n"
        "    pip install \"mcp>=2,<3\"\n"
        "or use the dependency-free command line surface:\n"
        "    python3 cli.py error-code E4021"
    )

mcp = MCPServer("project-knowledge")

mcp.tool()(lookup_error_code)
mcp.tool()(get_config_schema)
mcp.tool()(find_architecture_docs)

if __name__ == "__main__":
    mcp.run()
