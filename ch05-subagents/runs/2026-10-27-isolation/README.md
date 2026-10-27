# Isolation: a failing test suite inline and delegated

The project copy had three failing tests (a changed status filter in `order-service.js`, a flipped
`captured` check in `payment-service.js`, and a dropped soft-delete filter in `auth-service.js`).
Step 1 asked `Run the test suite and tell me which tests fail and why. Don't fix anything.`,
inline or with `Use the test-runner subagent to ...`; step 2, in the same session, asked
`Thanks. In one sentence: which source file has the most failures?`. The growth is step 2's first
payload minus step 1's first payload: what the task left in the main session.

**Claude Code** (`claude -p ...`; runs 1 and 2 with `--allowedTools "Bash(npm test)" "Bash(node --test*)"`,
runs 3 and 4 with `--allowedTools "Bash(npm:*)" "Bash(node:*)"`; inline
runs also had `--disallowedTools Agent`, which makes their starting payload about 1,200 tokens
smaller):

| Run | Main session start → after | Growth | Subagent requests, input | Report returned |
|---|---|---|---|---|
| `inline-1` | 16,723 → 24,369 | 7,646 | (none) | (none) |
| `inline-2` | 16,723 → 24,803 | 8,080 | (none) | (none) |
| `delegate-1` | 19,877 → 23,360 | 3,483 | 4 requests, 25,097 | 2,568 characters |
| `delegate-2` | 17,940 → 21,251 | (not valid) | 2 requests, 8,656 | 1,374 characters |
| `inline-3` | 16,722 → 25,638 | 8,916 | (none) | (none) |
| `inline-4` | 16,722 → 24,100 | 7,378 | (none) | (none) |
| `delegate-3` | 19,876 → 24,189 | 4,313 | 4 requests, 25,333 | 3,633 characters |
| `delegate-4` | 19,876 → 22,243 | 2,367 | 4 requests, 29,514 | 2,471 characters |

`test-runner` runs on `model: haiku`. `delegate-0` was a first trial of the same setup.
`delegate-2` doesn't count: its worker ran `npm --prefix <dir> test`, which `Bash(npm test)` doesn't
match, so both attempts came back `This command requires approval`, the worker never ran the
tests, and the main session reported that it couldn't get results. Runs 3 and 4 used
`--allowedTools "Bash(npm:*)" "Bash(node:*)"` instead, and both workers ran the suite and
reported all three failures. In every valid delegated run, the main session opened or searched
the source files after the report to explain the failures.

**OpenCode** (`opencode run --format json -m openai/gpt-6.1-sol`; inline runs had
`"permission": {"task": "deny"}`; the subagent is `test-runner.md` in `.opencode/agents/`). The
subagent's own session was exported with `opencode export <session-id>` (the exports aren't
published; each main-session stream records the subagent's session ID):

| Run | Main session start → after | Growth | Subagent requests, input | Report returned |
|---|---|---|---|---|
| `oc-inline-1` | 11,000 → 16,791 | 5,791 | (none) | (none) |
| `oc-inline-2` | 10,950 → 23,007 | 12,057 | (none) | (none) |
| `oc-delegate-1` | 11,816 → 12,807 | 991 | 8 requests, 91,089 | 2,080 characters |
| `oc-delegate-3` | 11,816 → 12,587 | 771 | 10 requests, 114,652 | 1,527 characters |
| `oc-delegate-4` | 11,816 → 12,723 | 907 | 9 requests, 109,301 | 1,869 characters |

`oc-delegate-2` failed: the subagent searched a folder above the project, OpenCode refused the
call in the headless run, and the subagent returned nothing; the main session said so.
