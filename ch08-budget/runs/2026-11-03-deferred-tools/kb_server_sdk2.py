"""Chapter 9's three tools on MCP SDK 2.0 (MCPServer), for the Chapter 8 deferral measurement only."""
import sys
sys.path.insert(0, "<companion>/ch09-mcp/server")
from tools import find_architecture_docs, get_config_schema, lookup_error_code
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("project-knowledge")
mcp.tool()(lookup_error_code)
mcp.tool()(get_config_schema)
mcp.tool()(find_architecture_docs)
if __name__ == "__main__":
    mcp.run()
