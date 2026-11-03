# Pricing: configuration size and a representative task

`<setup>-<n>.context.md` is `/context` before any prompt. `<setup>-<n>.task.*` is the task
`Add a function countPaidOrders(callback) to src/services/order-service.js that calls back with the
number of paid orders, in the same callback style as the other functions in that file, with a test.
Run npm test when you're done.`, run with `--permission-mode acceptEdits --allowedTools "Bash(npm test*)" "Bash(node --test*)"`.

| Setup | `/context` memory files | First request | Requests | Largest request | All input | Rules loaded | Tests after |
|---|---|---|---|---|---|---|---|
| none-1 | (none) | 31,457 | 6 | 36,705 | 204,357 | (none) | 12 pass |
| none-2 | (none) | 31,458 | 4 | 35,539 | 132,752 | (none) | 11 pass |
| monolithic-1 | 2k | 33,613 | 6 | 38,616 | 219,262 | (none) | 11 pass |
| monolithic-2 | 2k | 33,619 | 8 | 37,826 | 288,231 | (none) | 11 pass |
| pruned-1 | 443 | 32,101 | 5 | 35,834 | 167,111 | (none) | 11 pass |
| pruned-2 | 443 | 32,101 | 6 | 39,107 | 212,401 | (none) | 11 pass |
| split-1 | 256 | 31,904 | 5 | 36,154 | 167,280 | `test-conventions.md` | 11 pass |
| split-2 | 256 | 31,903 | 6 | 37,648 | 207,767 | `test-conventions.md` | 11 pass |

Every run's new test uses the `(t, done)` signature. The new function used `OrderRepository` in
`monolithic-1` and `pruned-2` and called `query()` directly in the other six, so the repository rule
was followed inconsistently with or without configuration (the task's "same callback style as the
other functions in that file" pulls the other way). `<setup>-<n>.diff` is each change.
