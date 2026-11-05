# Reading the traffic

Prompt: `The payments service is returning E4021 in staging. Find out what that means, check the configuration schema, and tell me what is likely misconfigured. Don't edit any files.` The server was registered through `tools/trace-stdio.py`. `trace-*.trace.jsonl` holds every message with its direction. Claude Code opened with `server/discover` at protocol version 2026-07-28; OpenCode with `initialize` at 2025-11-25.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in. Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed.

| Run | Correct diagnosis | Requests | Tool calls in order |
|---|---|---|---|
| cc-trace-1 | yes | 5 | ToolSearch, lookup_error_code, get_config_schema, Grep, Read, Read, Grep |
| oc-trace-1 | no | 3 | lookup_error_code, get_config_schema, find_architecture_docs |
