# Files versus the server on the staging task

Prompt: `The payments service is returning E4021 in staging. Find out what that means, check the configuration schema, and tell me what is likely misconfigured. Don't edit any files.` `files`: the knowledge written into `docs/` by `knowledge/render_docs.py`, no server. `mcp`: the stdio server registered, no `docs/`. *Growth* is the last request's input minus the first's. A diagnosis is correct when it names staging's `AUTH_HOLD_MINUTES=10` as shorter than the 15-minute capture delay.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in. Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed.

| Run | Correct diagnosis | Requests | Growth | Total input | Tool calls in order |
|---|---|---|---|---|---|
| cc-files-1 | yes | 3 | 5,462 | 107,078 | Grep, Glob, Read, Read, Read |
| cc-files-2 | yes | 4 | 4,162 | 141,383 | Grep, Bash, Read, Read, Read, Grep |
| cc-mcp-1 | yes | 4 | 1,811 | 136,456 | ToolSearch, lookup_error_code, get_config_schema, Grep |
| cc-mcp-2 | yes | 4 | 1,716 | 136,365 | ToolSearch, lookup_error_code, get_config_schema, Grep |
| oc-files-1 | yes | 5 | 5,170 | 67,284 | grep, glob, read, read, read, read, read, read |
| oc-files-2 | yes | 6 | 6,238 | 86,617 | read, glob, glob, glob, grep, read, read, grep, read, read, read, grep, read |
| oc-mcp-1 | no | 2 | 313 | 24,839 | lookup_error_code, get_config_schema |
| oc-mcp-2 | no | 2 | 313 | 24,835 | lookup_error_code, get_config_schema |
