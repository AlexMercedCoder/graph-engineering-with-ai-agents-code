# Deferred tool schemas

The three Chapter 9 tools, served by `kb_server_sdk2.py` (the Chapter 9 server ported to MCP Python
SDK 2.0, where `FastMCP` became `MCPServer`). `default-<n>`: tool search on, Claude Code's default.
`eager-<n>`: `ENABLE_TOOL_SEARCH=false`. `<mode>-<n>.task`: `Use the project-knowledge tools to look
up error code E4021 and tell me what it means. One sentence.`

| Mode | `/context` system tools sent | Deferred | MCP tools | Task requests (payloads) |
|---|---|---|---|---|
| default, both runs | 19.4k | 21.2k system, 338 MCP | deferred | 3 (31,524, 31,810, 31,925 and 31,525, 31,811, 31,926) |
| eager, both runs | 44.3k | none | 338 | 2 (56,320, 56,435 and 56,323, 56,438) |

The default sessions spent one request searching for the tool before calling it.
