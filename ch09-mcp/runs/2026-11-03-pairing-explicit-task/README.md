# The teaching skill, explicit staging task

Prompt: `The payments service is returning E4021 in staging. Find out what that means, check the configuration schema, and tell me what is likely misconfigured. Don't edit any files.` Skill installed. Compare with the `mcp` rows of `../2026-11-03-cost/`.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in, with the server registered as in the chapter (`KB_IDENTITY=engineer`). Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed. These runs use the skill with its step for a refused schema call.

| Run | Correct diagnosis | Requests | Total input | Tool calls in order |
|---|---|---|---|---|
| cc-skill-1 | yes | 6 | 208,392 | Skill, ToolSearch, lookup_error_code, find_architecture_docs, get_config_schema, Glob, Read |
| cc-skill-2 | yes | 6 | 208,382 | Skill, ToolSearch, lookup_error_code, find_architecture_docs, get_config_schema, Glob, Read |
| oc-skill-1 | yes | 6 | 78,751 | skill, lookup_error_code, find_architecture_docs, get_config_schema, read |
| oc-skill-2 | yes | 5 | 65,254 | skill, lookup_error_code, find_architecture_docs, get_config_schema, read |
