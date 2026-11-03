# Isolation rerun: the revised test-runner, 2026-11-03

The same exercise as `../2026-10-27-isolation/`, with `test-runner` changed to report, for each
failure, the source file and line responsible, the line itself, and one sentence on why it gives
the wrong result (`../../agents/test-runner.md`, `maxTurns: 12`). `opencode/test-runner.md` is the
OpenCode equivalent with the same body.

Setup: a fresh committed copy of `sample-project/` with three failing tests (the paid-orders
filter changed to `'quote'`, the uncaptured-payments filter inverted, and the soft-delete check
dropped from `findByEmail`). Step 1: `Run the test suite and tell me which tests fail and why.
Don't fix anything.`, prefixed with `Use the test-runner subagent to` for delegated runs. Step 2,
resumed in the same session: `Thanks. In one sentence: which source file has the most failures?`

- **Claude Code 2.1.316**, main model `claude-opus-5-5`: `claude -p ... --setting-sources project,local --allowedTools "Bash(npm:*)" "Bash(node:*)"`; inline runs also had `--disallowedTools Agent`.
- **OpenCode 1.19.5**, `openai/gpt-6.1-sol`: `opencode run --format json -m openai/gpt-6.1-sol ...`; inline runs had `"permission": {"task": "deny"}`.

Growth is step 2's first payload minus step 1's first payload (input plus cached tokens).

| Run | Main session start → after | Growth | Worker requests, input | Main session read source after the report? |
|---|---|---|---|---|
| `inline-1` | 28,042 → 37,147 | 9,105 | (none) | (inline) |
| `inline-2` | 28,033 → 39,627 | 11,594 | (none) | (inline) |
| `delegate-1` | 31,612 → 37,926 | 6,314 | 5, 42,908 | Yes: searched the three service files to confirm the causes |
| `delegate-2` | 31,604 → 36,393 | 4,789 | 5, 47,723 | No |
| `delegate-3` | 31,606 → 36,477 | 4,871 | 4, 33,630 | No |
| `delegate-4` | 31,605 → 36,122 | 4,517 | 5, 47,678 | No |
| `oc-inline-1` | 11,719 → 18,269 | 6,550 | (none) | (inline) |
| `oc-inline-2` | 11,719 → 19,899 | 8,180 | (none) | (inline) |
| `oc-delegate-1` | 12,532 → 13,705 | 1,173 | 13, 198,328 | No |
| `oc-delegate-2` | 12,532 → 13,466 | 934 | 8, 111,708 | No |
| `oc-delegate-3` | 12,532 → 13,599 | 1,067 | 14, 204,034 | No |
| `oc-delegate-4` | 12,480 → 13,506 | 1,026 | 6, 82,417 | No |

Every delegated report named all three failures with the responsible line and its cause. The
Claude Code baseline is about 12,000 tokens larger than in the October runs because 2.1.316 lists
more built-in skills; the growth figures are what to compare. Claude Code subagent transcripts
(`claude-code/subagents/`) keep user and assistant messages only. OpenCode worker sessions were
exported with `opencode export` to count their input; the exports aren't published. Local paths
are replaced with placeholders.
