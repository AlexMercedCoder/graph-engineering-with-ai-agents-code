# Namespacing and name collisions

`team-workflow` (and, where noted, `release-tools`) loaded with `--plugin-dir`. Read-only prompts ran
with the default permissions; `e4` added `--permission-mode acceptEdits` and the test and route-check
commands.

| Sessions | Setup | Prompt | Result |
|---|---|---|---|
| `e1a-1`, `-2` | team-workflow | `/team-workflow:code-review src/services/payment-service.js` | The plugin's review ran, both |
| `e1b-1`, `-2` | team-workflow | `/code-review src/services/payment-service.js` | Claude Code's built-in `code-review` skill ran instead (its multi-phase procedure starting from a diff), both |
| `e1c-1`, `-2` | team-workflow | `Review the changes in src/services/auth-service.js` | Skill call `team-workflow:code-review`, both |
| `e2-1` to `-3` | team-workflow, plus the project's own `.claude/skills/code-review` edited to begin with `LOCAL-COPY` | same | Project copy in `e2-1` and `e2-3` (reports begin `LOCAL-COPY`); plugin's in `e2-2` |
| `e3c-1`, `-2` | team-workflow | `Use the test-runner subagent to run the test suite and tell me which tests fail.` | Agent `team-workflow:test-runner`, both |
| `e3-1`, `-2` | team-workflow, plus the project's `.claude/agents/test-runner.md` edited to begin with `LOCAL test-runner` | same | Agent `test-runner` (the project's), both; both reports begin with the marker |
| `e6-1`, `-2` | team-workflow and release-tools (both ship `code-review`) | `Review the changes in src/services/auth-service.js` | `team-workflow:code-review`, both |
| `e4-1`, `-2` | team-workflow | `Use the module-migrator subagent to migrate src/services/order-service.js.` | Agent `team-workflow:module-migrator`; its transcript (`workers/`) holds the `migrate-module` skill body, preloaded by the bare name `skills: migrate-module`. Both edited `src/api/routes.js`, ran the route check, and ended with 10 tests passing and all 5 routes responding (`e4-<n>.routes`) |
| `e9plugin-1`, `-2` | a copy of team-workflow whose `test-runner` has a `hooks:` block that appends to `.agent-work/agent-hook-fired` on every Bash call | test-runner prompt | The worker ran `npm test`; the file was never created, both |
| `e9agents-1`, `-2` | the same definition, hooks included, passed with `--agents` | same | 3 lines written, both |
