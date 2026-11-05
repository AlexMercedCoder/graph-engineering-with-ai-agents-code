# Deferred tool schemas

Each session was asked only `Reply with the single word OK.` Settings: `none` (no server), `default` (server, tool search on), `always` (every tool marked `anthropic/alwaysLoad` in `_meta`), `eager` (`ENABLE_TOOL_SEARCH=false`). OpenCode has no deferral setting.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in. Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed.

| Run | First request |
|---|---|
| cc-always-1 | 33,587 |
| cc-always-2 | 33,589 |
| cc-default-1 | 33,098 |
| cc-default-2 | 33,101 |
| cc-eager-1 | 57,898 |
| cc-eager-2 | 57,897 |
| cc-none-1 | 33,002 |
| cc-none-2 | 33,005 |
| oc-default-1 | 12,233 |
| oc-default-2 | 12,235 |
| oc-none-1 | 11,835 |
| oc-none-2 | 11,835 |
