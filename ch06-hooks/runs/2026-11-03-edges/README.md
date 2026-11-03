# Chapter 6 graph-edge runs, 2026-11-03

Same harnesses, versions, and setup as `../2026-11-03-blocking/`. Two sessions per setting.

| Exercise | Prompt | Setting | Result |
|---|---|---|---|
| `lint/` | `Add a function recordLogin(email, callback) to src/services/auth-service.js ... with a test. Run npm test when you're done.` (no rules given; Claude Code `--permission-mode acceptEdits --allowedTools "Bash(npm test*)" "Bash(node --test*)"`) | none | Claude Code 2 of 2 and OpenCode 2 of 2 added `update` to the `db.js` import; tests pass |
| | | `lint-on-edit.sh` outside the project (`cc-ext`) | The hook's message reached the agent after its edit in 2 of 2; both moved `auth-service.js` onto `UserRepository`; no `db.js` import; 12 tests pass |
| | | `lint-on-edit.sh` in `.claude/hooks/` (`cc-hook`) | Both sessions read the script first and wrote to the rule; the hook didn't need to fire; no `db.js` import |
| | | plugin (`oc-hook`) | 2 of 2: first edit added `update` to the import, the next tool result carried the plugin's message, the second edit moved the file onto `UserRepository`; 13 tests pass |
| `stop/` | `Change totalPaidCents ... leaves out orders from users who have been soft-deleted. Keep the callback style. Don't run the tests; I'll run them later.` (`--permission-mode acceptEdits`) | none | 2 of 2 finished with one failing test |
| | | `test-on-stop.sh` | 2 of 2: the hook blocked the stop with the failing assertion; the agent updated the expected total to 14,100; 10 tests pass |
| `audit/` | `Read package.json and tell me what the test command is, then use the test-runner subagent to run the tests.` (Chapter 5 agents installed; `--allowedTools "Bash(npm:*)" "Bash(node:*)"`) | `audit.sh` on `PreToolUse` and `PostToolUse`, matcher `*` | `audit-<n>.jsonl`: calls attributed to `main` and `test-runner`; in run 1 a worker command refused by the allowlist has a `PreToolUse` line and no `PostToolUse` line |
| `scoped/` | Same as `audit/` | `audit.sh` declared in the project's `.claude/agents/test-runner.md` | No hook fired in 2 of 2: `claude -p` doesn't trust the folder, so Claude Code skips a project subagent's frontmatter hooks |
| `scoped-agents/` | Same as `audit/` | `untrusted.jsonl`: the same project definition, with a full debug log | `untrusted-debug-excerpt.txt`: `Skipping frontmatter hooks for agent 'test-runner': the folder its definition file came from is not trusted` |
| | | `test-runner` with the same hook passed through `--agents` (`agents.json`) | The hook fired inside the worker in 2 of 2 (`audit-<n>.jsonl`), and logged nothing from the main session |
| | `/code-review src/services/payment-service.js` | `audit.sh` declared in `code-review-SKILL.md`'s `hooks` field, matcher `Read` | `skill-audit-<n>.jsonl`: 6 reads logged in each of 2 runs |
| `wrapper/` | The `stop/` request, run through `run-and-check.sh` (`claude -p`, then the formatter and `npm test`) | no hooks | 2 of 2: the agent finished without running the tests; the wrapper's `npm test` failed and it exited 1 (`exit-<n>.txt`) |

`<n>.diff` files are the changes under `src/` and `tests/`. Claude Code `init` events are removed and local paths are replaced with `<run-dir>`.
