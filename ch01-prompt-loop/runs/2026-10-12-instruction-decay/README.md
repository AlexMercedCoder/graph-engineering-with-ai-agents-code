# Instruction-decay exercise: four real runs, 2026-10-12

Chapter 1's first exercise, run exactly as the chapter describes it: a fresh copy of
`sample-project/` per run, the project rule (`rule.txt`) sent as the first message, and the
task (`task.txt`) sent as the second message in the same session.

| Run | Harness | Model | Rule kept | Tests | Routes responding | Files changed | What stood out |
|---|---|---|---|---|---|---|---|
| `codex-1` | OpenAI Codex 0.159.0 (`codex exec`) | `gpt-6-sol` | Yes | 11 pass | 5 of 5 | 8 | Started migrating all four services after the rule message alone, before the task arrived |
| `codex-2` | OpenAI Codex 0.159.0 (`codex exec`) | `gpt-6-sol` | Yes | 12 pass | 5 of 5 | 8 | Also moved the auth and payment services, and added `payment-repository.js`, "to satisfy the project rule across `src/services/`" |
| `opencode-1` | OpenCode 1.18.31 (`opencode run`) | `deepseek-v4-flash` | Yes | 11 pass | 1 of 5 | 6 | Converted the services from callbacks to promises and rewrote the tests to match; `routes.js` still passes callbacks, so four endpoints never respond |
| `opencode-2` | OpenCode 1.18.31 (`opencode run`) | `deepseek-v4-flash` | Yes | 10 pass | 5 of 5 | 3 | Stayed within the two requested services |

None of the four sessions broke the project rule. Every agent ran its own search for `db.js`
imports before reporting back, and every one fixed the paid-total report through
`UserRepository`, moving it from 14,600 cents to 14,100. The sessions made between 15 and 26
tool calls each. The failure that did appear was an interface change that the unit tests never
exercised, which is why the exercise now ends with `node scripts/check-routes.js`.

Claude Code 2.1.284 and Pi 0.85.1 were attempted on the same day, but their sign-ins had
expired, so they have no runs here.

## Files in each run directory

| File | Contents |
|---|---|
| `turn1.jsonl`, `turn2.jsonl` | The harness's raw event stream for each message. Local paths are replaced with `<run-dir>`. |
| `changes.diff` | Everything the agent changed, against the unmodified sample project |
| `npm-test.txt` | `npm test` output after the session |
| `rule-grep.txt` | Step 5 of the exercise. No matches means the rule held. |
| `check-routes.txt` | `node scripts/check-routes.js` after the session |

To compare a run of your own, run the same two messages, then `npm test`, the `grep` from
step 5, and `node scripts/check-routes.js` inside `sample-project/`.
