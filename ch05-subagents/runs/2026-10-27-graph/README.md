# The shell execution graph, run for real

`../run-graph.sh src/services/order-service.js`, in fresh copies of `sample-project/` with the
Chapter 4 skills installed:

```bash
PROJECT_DIR=<copy> AGENT_CMD="claude -p --setting-sources project,local --permission-mode acceptEdits --allowedTools Bash(npm:*) Bash(node:*) Bash(mkdir:*)" ./run-graph.sh src/services/order-service.js
```

| Runs | Version of the script and nodes | Script's checks | Routes afterward | What node 3 (verify) said |
|---|---|---|---|---|
| `graph-1`, `graph-2` | Node 2's brief said `Change no other file`; the script checked module tests and `npm test` only | passed; printed `== graph complete` | 2 of 5 broken, both | Both reported that behavior outside the module had changed (for example, "Verdict: fails verification despite the green suite.") |
| `graph-3`, `graph-4` | Node 2 may update the callers in `src/api/routes.js`; the script also runs `node scripts/check-routes.js` after nodes 2 and 3 | passed | 5 of 5 respond, both | Both checks pass |

In `graph-1` and `-2`, node 2 kept to its module as told, `src/api/routes.js` kept calling the
migrated functions with callbacks, and the two routes that use them never answered. The script
can't read a node's verdict, only exit codes, so it reported success. `graph-<n>.log` is the
script's output, `graph-<n>.diff` the change, and `graph-<n>-test-failures.md` node 1's output.

`routes/` holds the output of `node scripts/check-routes.js` in each copy afterward. A trailing `timeout: the monitored command dumped core` line is Node crashing on exit on the author's machine, after the check printed its result.
