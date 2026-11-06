# Chapter 8 runs, 2026-11-03 and 2026-11-05

Claude Code 2.1.316 with `claude-opus-5-5`, headless with `--setting-sources project,local`,
`--strict-mcp-config`, and no MCP servers unless noted; OpenCode 1.19.5 with
`openai/gpt-6.1-sol`. Every session ran on a fresh committed copy of `sample-project/`. Each
setting ran twice. `<name>.jsonl` is the harness's stream output; `<name>.summary.json` lists the
per-request payloads and what Claude Code attached to the context (instruction files, path-scoped
rules, skill listing, compaction boundaries), extracted from the session file the way
`../loaded-context.py` does. The raw session files aren't published, because they hold account
details; the listings in the chapter were produced from them and match these summaries. `/context` output is in `<name>.context.md` or `<name>.md`.
Claude Code `init` events are removed; local paths are replaced with `<run-dir>`.

| Folder | What it measures |
|---|---|
| `2026-11-03-pricing/` | `/context` and the `countPaidOrders` task with no configuration, the 146-line guide (`../CLAUDE.monolithic.md`), the pruned file (`../CLAUDE.pruned.md`), and the split core with path-scoped rules |
| `2026-11-03-triggers/` | Which actions on `src/api/routes.js` load the path-scoped API rule (seven requests) |
| `2026-11-03-compaction/` | Whether `CLAUDE.md` and a loaded path-scoped rule come back after `/compact`, with no-compaction controls |
| `2026-11-03-single-process/` | The rule and skill compaction tests inside one continuous process |
| `2026-11-03-skill-compaction/` | Whether an invoked skill's body comes back after `/compact` (slash command and Skill tool, 9,000 and 1,700 tokens) |
| `2026-11-03-listing/` | `/context` skill listing cost for 4 to 160 project skills (`synth.py`), the compressed and grouped variants, and 48 skills in 6 groups |
| `2026-11-03-skill-paths/` | A skill with a `paths` field, before and after a matching read |
| `2026-11-03-deferred-tools/` | `/context` and a lookup task with an MCP server, with tool search on (default) and off (`ENABLE_TOOL_SEARCH=false`) |
| `2026-11-03-opencode-loading/` | The same configurations as `AGENTS.md` in OpenCode, and the pointer-line substitute for path-scoped rules |
| `2026-11-03-routing/` | Chapter 4's twenty prompts against the flat, compressed, and grouped skills, twice per harness |
| `2026-11-05-budget-check/` | `../check-budget.py` against the split configuration (passes) and the 146-line guide (fails) |
| `2026-11-05-names-only/` | Chapter 4's twenty prompts with the four skills listed by name only, against a same-day control with full descriptions |
| `2026-11-05-skills-vs-inline/` | The book's own manuscript configuration with its guidance in skills against the same guidance inline in `CLAUDE.md` |
| `2026-11-05-opencode-nested-rules/` | OpenCode loading a subdirectory's `AGENTS.md` when the agent reads a file there |
