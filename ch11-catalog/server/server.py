"""The Chapter 11 governed-data MCP server (MCP Python SDK 2.x).

    pip install -r requirements.txt
    CATALOG_IDENTITY=analyst CATALOG_SCOPES="catalog:read data:read" python3 server/server.py

Over stdio, identity and scopes come from the environment the client launches the
server with. Over HTTP they would come from the verified access token, as in
Chapter 9. Tools are registered only for the scopes granted, so an agent without
data:read never sees execute_query at all.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import execute_query, generate_governed_sql, navigate_catalog, scopes  # noqa: E402

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # pragma: no cover
    raise SystemExit("The MCP SDK 2.x is not installed:  pip install -r requirements.txt\n"
                     "Or use the command line surface:  python3 server/cli.py navigate premium")

mcp = MCPServer("governed-data")
granted = scopes()
if "catalog:read" in granted:
    mcp.tool()(navigate_catalog)
    mcp.tool()(generate_governed_sql)
if "data:read" in granted:
    mcp.tool()(execute_query)

if __name__ == "__main__":
    mcp.run()
