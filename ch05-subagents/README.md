# Chapter 5: Solving Multi-Task Interference

| Path | What it is |
|---|---|
| `agents/test-runner.md` | Runs the suite and reports only failures; no edit tools (but `Bash`), `model: haiku`, `maxTurns: 8` |
| `agents/module-migrator.md` | Migrates one module (preloads the `migrate-module` skill) and returns a four-line report |
| `agents/migration-dispatcher.md` | Sends one module per `module-migrator`, assembles their reports, and then has one agent fix the callers in `src/api/routes.js`; no edit tools itself |
| `nodes/` and `run-graph.sh` | The same work as a shell execution graph: one fresh session per node, with each node's success condition checked by the script |
| `runs/` | Real runs from 2026-10-27; see `runs/README.md` |

Install the agents with `cp agents/*.md <project>/.claude/agents/` (Claude Code) and the Chapter 4
skills with `cp ../ch04-routing/skills/* <project>/.claude/skills/ -r`. `module-migrator` preloads
`migrate-module`, so the skill must be installed.

`run-graph.sh` prints a dry run without `AGENT_CMD`. To run it with Claude Code on a copy of the
project:

```bash
PROJECT_DIR=<copy> AGENT_CMD="claude -p --setting-sources project,local --permission-mode acceptEdits --allowedTools Bash(npm:*) Bash(node:*) Bash(mkdir:*)" ./run-graph.sh src/services/order-service.js
```

`AGENT_CMD` is split on spaces, so write tool patterns without spaces (`Bash(npm:*)`).
