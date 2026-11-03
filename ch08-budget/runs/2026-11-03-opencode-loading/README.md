# OpenCode: configuration as AGENTS.md, and the pointer-line substitute

The same configurations as `AGENTS.md`. `pointer`: the core from `../../CLAUDE.core.md` plus a line
pointing to `docs/rules/api.md`, `repositories.md`, and `tests.md` (the three rules without their
frontmatter). `<setup>-<n>.task`: the same `countPaidOrders` task as the Claude Code pricing runs.
`pointer-route-<n>`: `Add a route GET /reports/paid-count to src/api/routes.js that answers with the
number of paid orders, using the order service. Follow the project's conventions. Run npm test and
node scripts/check-routes.js when you're done.`

| Run | First request | Rule files read | Tests after | New code used `OrderRepository` |
|---|---|---|---|---|
| none-1, none-2 | 11,870 | (none) | 11, 12 pass | No, both |
| monolithic-1, -2 | 13,253 | (none) | 11, 12 pass | Yes, both |
| pruned-1, -2 | 12,228 | (none) | 11 pass, both | Yes, both |
| pointer-1, -2 | 12,136 and 12,134 | `tests.md`, `repositories.md` (both) | 11 pass, both | Yes, both |
| pointer-route-1, -2 | 12,138 | `api.md`, `repositories.md` (both) | 10 pass, all 6 routes respond, both | Yes, both |

Every new test uses the `(t, done)` signature. OpenCode was started with `--dir <run-dir>`.
