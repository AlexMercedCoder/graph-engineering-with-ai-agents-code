# Streamable HTTP with bearer tokens

Prompt: `The payments service is returning E4021 in staging. Find out what that means, check the configuration schema, and tell me what is likely misconfigured. Don't edit any files.` `server/http_server.py` on 127.0.0.1:8765 with tokens from `tools/make-test-tokens.py` (not published). `operator`: `knowledge:read schema:read`. `engineer`: `knowledge:read` only, so `get_config_schema` gets a 403. Claude Code surfaced it as the tool error `Insufficient scope: required "knowledge:read schema:read"`; OpenCode reported `ECONNREFUSED` while trying to reach the authorization server named in the metadata. `oc-403-step-up.jsonl` and `oc-403-authorization-server.log` repeat one OpenCode call with a stub listening on the issuer port, which logged the discovery and registration requests OpenCode sent.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in. Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed.

| Run | Correct diagnosis | Requests | Total input | Tool calls in order |
|---|---|---|---|---|
| cc-engineer-1 | yes | 6 | 207,957 | ToolSearch, lookup_error_code, get_config_schema, Grep, find_architecture_docs, Read, Read, Grep |
| cc-engineer-2 | yes | 6 | 208,699 | ToolSearch, lookup_error_code, get_config_schema, Grep, find_architecture_docs, Bash, Grep, Grep |
| cc-operator-1 | yes | 4 | 136,285 | ToolSearch, lookup_error_code, get_config_schema, Grep |
| cc-operator-2 | yes | 4 | 136,353 | ToolSearch, lookup_error_code, get_config_schema, Grep |
| oc-engineer-1 | no | 4 | 50,300 | lookup_error_code, get_config_schema, find_architecture_docs, get_config_schema |
| oc-engineer-2 | yes | 5 | 65,742 | lookup_error_code, get_config_schema, get_config_schema, glob, read, read, read |
| oc-operator-1 | no | 2 | 24,827 | lookup_error_code, get_config_schema |
| oc-operator-2 | no | 2 | 24,835 | lookup_error_code, get_config_schema |
