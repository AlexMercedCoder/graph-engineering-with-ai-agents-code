# Other harnesses, November 5, 2026

The chapter's comparisons ran in Claude Code and OpenCode. These runs check that the same stdio
server works in OpenAI Codex and Pi, without changing any user configuration.

- `codex-default-approval.jsonl`: Codex CLI 0.166.0, `codex exec -s read-only`, server registered
  with `-c mcp_servers.project-knowledge.*` overrides. The tool call failed with
  `MCP tool call requires approval, but approval policy is never`.
- `codex-approve.jsonl`: the same with
  `-c 'mcp_servers.project-knowledge.default_tools_approval_mode="approve"'`. The call returned
  `Payment authorization expired`, E4021's title.
- `pi-mcp-list.txt`: Pi 1.4.0 with `PI_CODING_AGENT_DIR` pointed at a scratch folder holding
  `mcp.json`. A project's `.pi/mcp.json` was ignored until the project is trusted.
- `time-calls.txt`: four runs of `python3 tools/time-calls.py 50`, startup and per-call latency of the
  stdio server (startup 1.0 to 1.4 s; median call 1.3 to 1.8 ms; `grep` 1.8 to 2.2 ms).

Google Antigravity (`agy` 1.4.12) was not run: its `agy mcp add` writes to the user's own
configuration, and its help lists no project-level file or option to point it at a scratch folder.
