# The teaching skill, vague request

Prompt: `Staging has been throwing E4021 on a lot of orders since this morning. What's going on? Don't edit any files.` `skill` adds `skills/diagnose-staging-error/` under `.claude/skills/`.

Run on November 3, 2026, on fresh copies of `sample-project/` with `exercise/config/` copied in, with the server registered as in the chapter (`KB_IDENTITY=engineer`). Claude Code 2.1.316 (`claude-opus-5-5`) ran headless with `--setting-sources project,local --strict-mcp-config --mcp-config .mcp.json`; OpenCode 1.19.5 (`openai/gpt-6.1-sol`) ran `opencode run --format json` with the server in the project's `opencode.json`. Paths are replaced with `<run-dir>`, and session `init` records are removed. These runs use the skill with its step for a refused schema call.

| Run | Correct diagnosis | Requests | Total input | Tool calls in order |
|---|---|---|---|---|
| cc-noskill-1 | yes | 5 | 175,628 | ToolSearch, Bash, lookup_error_code, Bash, Bash, Read, Read, Read, Read, get_config_schema |
| cc-noskill-2 | yes | 4 | 137,959 | ToolSearch, Bash, lookup_error_code, Bash, Bash, get_config_schema |
| cc-skill-1 | yes | 7 | 243,849 | Skill, ToolSearch, lookup_error_code, find_architecture_docs, get_config_schema, Glob, Read, Read |
| cc-skill-2 | yes | 7 | 243,990 | Skill, ToolSearch, lookup_error_code, find_architecture_docs, get_config_schema, Glob, Read, Bash |
| oc-noskill-1 | yes | 8 | 106,253 | lookup_error_code, read, find_architecture_docs, glob, glob, read, read, read, bash |
| oc-noskill-2 | yes | 7 | 94,726 | lookup_error_code, find_architecture_docs, bash, glob, read, read, read, bash |
| oc-skill-1 | yes | 7 | 92,292 | skill, lookup_error_code, find_architecture_docs, get_config_schema, glob, read |
| oc-skill-2 | yes | 6 | 78,707 | skill, lookup_error_code, find_architecture_docs, get_config_schema, read |
