# Chapter 3 task ladder: eight real runs, 2026-10-22

The ladder from `../../task-ladder.md`, run in Claude Code 2.1.308 (`claude-opus-5-5`,
`claude -p` with `--permission-mode acceptEdits --allowedTools Bash`) and OpenAI Codex 0.162.1
(`gpt-6-sol`, `codex exec --sandbox workspace-write`), each as one continuous session (`*-cont-*`)
and as a fresh session per task with the rules restated (`*-fresh-*`), twice. `score-task.sh`
scored and committed every task.

| Setup | Requests | Input tokens, seven tasks | Share cached | Peak payload, task 7 | Tasks with all three rules kept |
|---|---|---|---|---|---|
| Claude Code, one session | 25 to 29 | 1.15M to 1.42M | 95% to 96% | 72,741 and 74,663 | 7 of 7 in both runs* |
| Claude Code, fresh sessions | 36 to 37 | 1.30M to 1.32M | 86% | 43,898 and 44,906 | 6 of 7 in both runs |
| OpenAI Codex, one session | 35 to 36 | 1.53M to 1.76M | 95% to 97% | 63,095 and 78,721 | 7 of 7 in both runs |
| OpenAI Codex, fresh sessions | 47 to 48 | 1.13M to 1.15M | 88% | 38,406 and 30,445 | 7 of 7 in both runs |

\* `cc-cont-1/scores.txt` shows task 2 at 2 of 3: the agent changed `listActiveUsers` without
adding a test, and the function already had one, so the chapter counts it as passing.

The two fresh Claude Code misses are real: on task 7, both runs rewrote the import line in
`src/services/user-service.js` and kept `update` from `../db.js` (see `cc-fresh-*/changes.diff`).

Baseline payload, with the rules sent and nothing read: about 31,300 tokens in Claude Code (the
author's configuration loads several skills and plugins; Claude Code's `/context`, run headless in
a fresh copy of `sample-project/` on the same day, counted 8,700 tokens of skills and about 1,600
of loaded MCP tools and server instructions) and about 20,300 in OpenAI Codex.

**Compaction test** (`cc-cont-*`): after task 7, `/compact` took the conversation from 74,159 to
16,450 tokens and from 75,418 to 16,776 (`compact.jsonl`, `compact_boundary` event). Both
summaries kept the three rules verbatim (`compaction-summary.txt`, exported from Claude Code's
session transcript), and the probe task (`probe.jsonl`) kept all three. Each session then took
the harder probe on `auth-service.js` (`probe2.jsonl`), and both kept all three rules again. The
OpenAI Codex continuous runs got the first probe with no compaction (`exec` has no `/compact`).
Neither probe shows that the rules survived: sessions with no rules at all passed the harder one,
and the first targets `order-service.js`, which task 4 had already migrated;
`../2026-10-22-compaction/` has the control runs and a probe (`recordLogin`) that does.

Files: Claude Code runs keep the `stream-json` output per step, minus `init` events (the local
skills, plugins, and MCP servers) and thinking-token counters. OpenAI Codex runs keep the
`exec --json` output per step and `codex-requests.csv`, the per-request payload extracted from
the session logs, which aren't published because they include local configuration. Every run has
`scores.txt` and `changes.diff`. Local paths are replaced with placeholders.
