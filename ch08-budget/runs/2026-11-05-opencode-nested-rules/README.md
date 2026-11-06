# OpenCode loads a subdirectory's AGENTS.md with the first file read there

OpenCode 1.19.5 with `openai/gpt-6.1-sol`, November 5, 2026, on a fresh copy of `sample-project/`
with one file added, `src/api/AGENTS.md`:

```markdown
# API rules

- Every route handler must log the marker string ZEBRA-7731 before calling back.
```

- `read-1.jsonl`, `read-2.jsonl`: "Read src/api/routes.js, then list every project instruction you
  have been given that applies to route handlers, quoting each exactly." In both, the read tool's
  output carried the rule after the file's contents, and the agent quoted it.
- `control.jsonl`: the same question without reading any file. The agent answered "none".
