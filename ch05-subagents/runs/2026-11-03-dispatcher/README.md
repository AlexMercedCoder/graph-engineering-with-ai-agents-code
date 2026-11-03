# Dispatcher rerun with the revised migrate-module skill, 2026-11-03

Claude Code 2.1.316, main model `claude-opus-5-5`. Every run used a fresh committed copy of
`sample-project/` with the Chapter 4 skills (the revised `migrate-module`, which names the routes
that call the target module as part of its job) and this chapter's agents.
`migration-dispatcher.md` and `module-migrator.md` here are the definitions used: the dispatcher has no callers step, and the worker updates the routes that call its module, runs the route check, and reports another module's failing route under `BLOCKERS`.

Prompts: `single-*` (with `--disallowedTools Agent`): `Migrate every module in src/services/ to the
repository pattern, one module at a time, running each module's tests as you go.` `dispatch-*`:
`Use the migration-dispatcher subagent to migrate every module in src/services/ to the repository
pattern.` All: `claude -p ... --setting-sources project,local --permission-mode acceptEdits
--allowedTools "Bash(node --test*)" "Bash(npm test*)" "Bash(mkdir *)" "Bash(ls *)" "Bash(node scripts/check-routes.js*)"`.

| Run | Tests after | Routes after | Main session peak, total input | Subagent sessions, their peaks, their input | All input |
|---|---|---|---|---|---|
| `single-1` | 10 pass | all 5 respond | 47,053, 490,721 | (none) | 490,721 |
| `single-2` | 10 pass | all 5 respond | 45,471, 611,692 | (none) | 611,692 |

`single-2` migrated three modules and stopped before `auth-service.js`, reporting that it needed a lookup by email on `UserRepository`, which the skill's file list doesn't allow; `auth-service.js` still imports `db.js` there. `single-1` filtered `findActive()` by email inside the service. (In `summary.txt`, the `single-2` route line shows Node crashing on exit after the check; rerun in that copy, the check reports all 5 routes respond.)
| `dispatch-1` | 10 pass | all 5 respond | 42,042, 185,414 | 5 (dispatcher and four workers), 10,255 to 14,852, 301,258 | 486,672 |
| `dispatch-2` | 10 pass | all 5 respond | 39,892, 257,551 | 5, 10,395 to 14,891, 352,959 | 610,510 |

What the transcripts show (`workers/<run>/`, user and assistant messages only):

- Every worker whose module a route calls edited `src/api/routes.js`; the auth workers didn't, because no
  route calls `auth-service.js`. Every worker ran `node scripts/check-routes.js`.
- Workers saw other workers' half-finished changes. In `dispatch-1`, the order and payment workers' route
  checks failed on routes belonging to modules still being migrated. In `dispatch-2`, the auth worker
  found `GET /reports/paid-total` never answering and `GET /reports/uncaptured-total` throwing, traced
  them to the order and payment modules, and reported them under `BLOCKERS`; the user worker saw two
  routes fail the same way. The dispatcher reported both as failures in modules that had reported
  complete. The main session's own route check afterward passed.
- `UserRepository` has no lookup by email, and the skill's file list doesn't allow editing
  `user-repository.js`. Both auth workers filtered `findActive()` by email in the service, reported
  `complete`, and noted the gap only in `.agent-work/migration/auth-service.md`.
- In both dispatcher runs, the main session said it would check the result itself and read the diff and
  ran the tests (and, in `dispatch-2`, the route check).

An earlier pair of dispatcher runs the same day used a `module-migrator` whose step 3 ran only the
module's tests (the skill still asked for the route check); they showed the same collisions and aren't
published separately.

`summary.txt` has each copy's outcome; `<run>.diff` is the full change.
