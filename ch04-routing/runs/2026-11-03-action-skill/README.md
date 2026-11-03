# Chapter 4 action-skill reruns, 2026-11-03

The `migrate-module` skill as it now stands in `../../skills/migrate-module/SKILL.md`: it names
the files it may edit (the target service and its test, the routes in `src/api/routes.js` that
call the target's functions, and `payment-repository.js` for the payment module), updates those
routes, and runs both the module's tests and `node scripts/check-routes.js`.

Each run used a fresh committed copy of `sample-project/` with the four skills in `.claude/skills/`.

| Session | Harness | Command | Tests after | Route check | Files changed |
|---|---|---|---|---|---|
| `mig-1`, `mig-2` | Claude Code 2.1.316, `claude-opus-5-5` | `claude -p "/migrate-module src/services/order-service.js" --setting-sources project,local --permission-mode acceptEdits --allowedTools "Bash(node --test*)" "Bash(npm test*)" "Bash(node scripts/check-routes.js*)"` | 10 pass, both | all 5 routes respond, both | `src/api/routes.js`, `src/services/order-service.js`, `tests/order-service.test.js`, both |
| `oc-mig-1`, `oc-mig-2` | OpenCode 1.19.5, `openai/gpt-6.1-sol` | `opencode run --format json -m openai/gpt-6.1-sol "Use the migrate-module skill to migrate src/services/order-service.js."` | 10 pass, both | all 5 routes respond, both | same three files, both |

Both OpenCode sessions loaded the skill through the `skill` tool and ran
`node --test tests/order-service.test.js && node scripts/check-routes.js`.

The earlier version of the skill, without the file list, step 4, or the route check, is in
`../2026-10-27-access/action-skill/`: both runs there also edited `src/api/routes.js`, which
that version never mentioned.

`summary.txt` has each copy's test result, route check, remaining `db.js` importers, and changed
files; `<session>.diff` is the full change. Claude Code `init` events are removed and local
paths are replaced with placeholders.
