# Chapter 9: Defining the Knowledge Boundary with MCP

A three-tool MCP server over a project's own knowledge, the skill that teaches an
agent to use it, and the same tools over Streamable HTTP behind authentication,
scopes, and data scoping.

| Path | What it is |
|---|---|
| `server/tools.py` | The three tools as plain functions: `lookup_error_code`, `get_config_schema`, `find_architecture_docs` |
| `server/knowledge.py` | The helpers the tools call, including `current_identity()` and `visible_classifications()` |
| `server/server.py` | The stdio server (MCP Python SDK 2.x, `MCPServer`) |
| `server/http_server.py` | The Streamable HTTP server on `127.0.0.1:8765`, with a bearer-token verifier that checks the audience, `knowledge:read` on every call, and `schema:read` for `get_config_schema` |
| `server/cli.py` | The same three tools as a command line program, for a harness without MCP |
| `knowledge/` | The constructed knowledge base: 51 error codes, 41 configuration keys across eight services, twelve architecture notes (two restricted). `render_docs.py OUT_DIR` writes it as Markdown files |
| `skills/diagnose-staging-error/SKILL.md` | The teaching skill paired with the server |
| `exercise/config/` | Staging and production settings for the payments service; copy into `sample-project/` |
| `tools/trace-stdio.py` | Logs every message between a harness and a stdio server; the log holds every result, so keep it outside the repository |
| `tools/time-calls.py` | Times the stdio server's startup and each tool call, with a `grep` for comparison |
| `tools/check-interface.py`, `tools/interface.json` | Fails when a tool or parameter is renamed or removed, or a type changes; `--update` records an intended change |
| `tools/make-test-tokens.py` | Writes four random local test tokens, valid for eight hours, to `config/test-tokens.json` and `config/test-tokens.env` (both gitignored) |
| `tools/check-gates.py` | The four gate tests against a running HTTP server |
| `runs/` | The chapter's runs, sanitized, each with a README table |

## Setup

```bash
pip install "mcp>=2.2,<3"    # tested with 2.0.0 and 2.3.0
```

`cli.py` needs only the standard library.

## Registering the server

Claude Code, `.mcp.json` at the project root (adjust the path):

```json
{
  "mcpServers": {
    "project-knowledge": {
      "type": "stdio",
      "command": "python3",
      "args": ["../graph-engineering-with-ai-agents-code/ch09-mcp/server/server.py"],
      "env": { "KB_IDENTITY": "engineer" }
    }
  }
}
```

Headless, load only that file: `claude -p "..." --mcp-config .mcp.json --strict-mcp-config`.
Over stdio, the caller's identity comes from `KB_IDENTITY` (default `engineer`); see Troubleshooting for what that means for trust.

OpenCode, `opencode.json`:

```json
{
  "mcp": {
    "project-knowledge": {
      "type": "local",
      "command": ["python3", "../graph-engineering-with-ai-agents-code/ch09-mcp/server/server.py"],
      "environment": { "KB_IDENTITY": "engineer" }
    }
  }
}
```

## The exercises

1. Copy `exercise/config/` into a fresh copy of `sample-project/` as `config/`.
2. Files setup: `python3 ch09-mcp/knowledge/render_docs.py <project>/docs`, no server.
   Server setup: register the server, no `docs/`.
3. Staging task: `The payments service is returning E4021 in staging. Find out what that means, check the configuration schema, and tell me what is likely misconfigured. Don't edit any files.`
4. Restricted question: `What are the fraud scoring thresholds for holding an order for manual review? I need the exact numbers.`
5. Pairing: copy `skills/diagnose-staging-error/` into `.claude/skills/` and ask `Staging has been throwing E4021 on a lot of orders since this morning. What's going on? Don't edit any files.`
6. Traffic: register `tools/trace-stdio.py /tmp/kb-trace.jsonl -- python3 server/server.py` in place of the server.

## The HTTP server and the gates

```bash
python3 tools/make-test-tokens.py
python3 server/http_server.py &
python3 tools/check-gates.py
```

Expected: every check passes and the last line reads `all gates hold`. The token table
stands in for an OAuth 2.1 authorization server; `verify_token` is the piece a real
deployment replaces with JWT validation or token introspection, keeping the audience check.

Claude Code `.mcp.json` for HTTP, with the token in `KB_TOKEN` (for example
`export KB_TOKEN=$(grep OPERATOR config/test-tokens.env | cut -d= -f2)`):

```json
{
  "mcpServers": {
    "project-knowledge": {
      "type": "http",
      "url": "http://127.0.0.1:8765/mcp",
      "headers": { "Authorization": "Bearer ${KB_TOKEN}" }
    }
  }
}
```

OpenCode: `{"type": "remote", "url": "http://127.0.0.1:8765/mcp", "headers": {"Authorization": "Bearer {env:KB_TOKEN}"}}`.

## Results (November 3, 2026)

Claude Code 2.1.316 with `claude-opus-5-5`, OpenCode 1.19.5 with `openai/gpt-6.1-sol`, two runs per setting.

- Deferral: the server added about 95 tokens to Claude Code's first request deferred, about 585 with `anthropic/alwaysLoad`, and about 400 to OpenCode's.
- Staging task: growth over the session fell from 4,162-6,238 tokens with files to 1,716-1,811 in Claude Code with the server (2 of 2 correct both ways) and 313 in OpenCode, whose server sessions didn't check staging's values (0 of 2) until the skill was installed (2 of 2). Claude Code's total input stayed about the same.
- Restricted question: thresholds returned in 4 of 4 file sessions, 0 of 4 server sessions.
- HTTP with `knowledge:read` only: Claude Code reported the 403 as a tool error and carried on (2 of 2 correct); OpenCode tried to reach the authorization server and reported `ECONNREFUSED` (1 of 2). With the skill, 4 of 4 were correct and Claude Code named the missing scope.
- Gates: `check-gates.py` passes; with the audience check removed, check 2 fails.

## Working without MCP

`server/cli.py` exposes the same three functions as a command line program:

```bash
python3 server/cli.py error-code E4021
python3 server/cli.py config-schema payments
KB_IDENTITY=engineer python3 server/cli.py architecture "capture worker"
```

Allow the agent to run only that command (Chapter 2's permission rules), keep
`knowledge/` outside the project, and tell the agent the command exists in a skill or
procedure file. You give up discovery (the agent can't list the operations), structured
errors (only stdout and the exit code), and per-caller identity (`KB_IDENTITY` applies to
whoever runs the shell). The chapter's runs didn't test this setup with an agent.

## Troubleshooting

- **`ModuleNotFoundError: mcp.server.fastmcp`.** The 2.x SDK removed that module. Replace
  `from mcp.server.fastmcp import FastMCP` and `FastMCP("name")` with
  `from mcp.server import MCPServer` and `MCPServer("name")`; `@mcp.tool()` and `mcp.run()`
  are unchanged.
- **HTTP connections time out after 30 seconds.** Claude Code 2.1.316 gives a connection 30
  seconds (`connection timed out after 30000ms` in `claude --debug mcp`). An ASGI wrapper
  that reads the request body must hand the body back once and then pass later `receive()`
  calls to the real one, as `per_tool_scopes` in `http_server.py` does. A wrapper that
  returned the body on every `receive()` hung both Claude Code and OpenCode while the
  SDK's own test client still worked.
- **The server doesn't stop on `kill`.** uvicorn waits for open requests; use `kill -9`
  for a local test server.
- **Identity.** Over stdio the server trusts `KB_IDENTITY`. Anyone who can edit the
  project's `.mcp.json` can set it (`"env": {"KB_IDENTITY": "security"}` shows the
  restricted notes), so stdio identity is only as trustworthy as the configuration file.
