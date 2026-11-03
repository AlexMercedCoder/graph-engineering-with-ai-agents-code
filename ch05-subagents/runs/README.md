# Chapter 5 runs, 2026-10-27

Claude Code 2.1.308 with `claude-opus-5-5` as the main model, and OpenCode 1.19.0 with
`openai/gpt-6.1-sol`. Every session ran on a fresh copy of `sample-project/` with the Chapter 4
skills in `.claude/skills/` and this chapter's agents in `.claude/agents/`. Payloads are input
plus cached tokens per model request. Claude Code `init` events, thinking-token counters, and
internal session records are removed; local paths, the author's email, and plan details are
replaced or removed.

| Folder | What it tests |
|---|---|
| `2026-10-27-isolation/` | Running a failing test suite inline versus through a `test-runner` subagent, in Claude Code and OpenCode |
| `2026-10-27-dispatcher/` | Migrating all four services in one session versus through `migration-dispatcher` and `module-migrator` workers |
| `2026-10-27-team/` | The same migration as a Claude Code agent team with a shared task list |
| `2026-10-27-team-2/` | A team that had to message between teammates: two modules and a router owner |
| `2026-10-27-memory/` | A `test-runner` subagent with `memory: project`, run twice |
| `2026-10-27-graph/` | `../run-graph.sh` run for real with headless Claude Code |
| `2026-10-27-resume/` | Resuming a finished `test-runner` with `SendMessage` |
| `2026-11-03-isolation/` | The isolation exercise again with the revised `test-runner`, which reports each failure's cause and line, in Claude Code 2.1.316 and OpenCode 1.19.5 |
| `2026-11-03-dispatcher/` | The dispatcher and single-session migration again with the revised `migrate-module` skill and no callers step, in Claude Code 2.1.316 |

The October runs used the earlier `test-runner` (failures and locations only) and the earlier `migrate-module` (no file list or route check); the October dispatcher runs needed a final callers step for that reason.
