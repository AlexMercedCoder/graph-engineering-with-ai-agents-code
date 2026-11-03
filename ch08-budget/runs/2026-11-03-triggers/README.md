# What loads a path-scoped rule

Split configuration (`../../CLAUDE.core.md` as `CLAUDE.md`, `../../rules/` in `.claude/rules/`).
Allowed shell commands: `cat`, `grep`, `node`, `ls`, `find`, `wc`.

| Prompt key | What the agent did | Rule loaded (both runs) |
|---|---|---|
| `read-api` | Read tool on `src/api/routes.js` | `api-conventions.md` |
| `cat-api` | `cat src/api/routes.js` | `api-conventions.md` |
| `grep-api` | `grep -c handler src/api/routes.js` (prints a count) | none |
| `grep-lines` | `grep handler src/api/routes.js` (prints matching lines) | `api-conventions.md` |
| `node-api` | `node -e "import('./src/api/routes.js')..."` | none |
| `read-test` | Read tool on `tests/order-service.test.js` | `test-conventions.md` |
| `open-question` | `grep` over `src`, then the Read tool on `src/api/routes.js` | `api-conventions.md`, after the read |
