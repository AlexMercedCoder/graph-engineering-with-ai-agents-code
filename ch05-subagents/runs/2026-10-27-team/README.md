# Agent team: the four-module migration with a shared task list

Claude Code 2.1.308, interactive (agent teams don't run under `claude -p`), started in `tmux` with
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and:

```bash
claude --setting-sources project,local --permission-mode dontAsk --allowedTools Read Edit Write Glob Grep Agent TaskCreate TaskGet TaskList TaskUpdate SendMessage TeamCreate TeamDelete 'Bash(node --test*)' 'Bash(npm test*)' 'Bash(mkdir *)' 'Bash(ls *)' 'Bash(git status*)' 'Bash(git diff*)'
```

A first attempt without the task and team tools in `--allowedTools` stopped before starting: in
`dontAsk` mode, the lead couldn't use them and said so. The prompt:

> Create an agent team with three teammates to migrate the four modules in src/services/ from
> callback-style database access to the repository pattern, creating a repository class for any
> table that doesn't have one. Put one task per module on the shared task list, plus a final
> task, blocked on the four, to run the full test suite. Each teammate claims tasks from the
> list, migrates that module and its test file, and runs that module's tests. If a change
> affects another module, message the teammate who owns it. When every task is complete, give
> me a table of modules, owners, and test results.

What happened, from the transcripts (`lead.jsonl`, `migrator-a.jsonl`, `-b`, `-c`; user and
assistant messages only) and the lead's screen (`lead-screen.txt`):

- The lead created five tasks with `TaskCreate`, made task 5 depend on tasks 1 to 4 with
  `TaskUpdate` (`addBlockedBy`), and spawned three teammates.
- Each teammate claimed tasks with `TaskUpdate` (`owner`, `status: in_progress`) and marked them
  `completed` with test results in `metadata`: migrator-a took tasks 1 and 4 (auth, user),
  migrator-b task 2 (order), migrator-c task 3 (payment, creating `PaymentRepository`).
- Task 5 was claimed twice: migrator-a set it in progress, and migrator-b, asked by the lead,
  claimed and completed it. Both ran the suite.
- No teammate messaged another teammate; all `SendMessage` calls went to or from the lead.
- The lead's `dontAsk` allowlist didn't hold the teammates consistently. migrator-a's commands
  outside it (a `node -e` route check, then `npm run lint` with `node scripts/check-routes.js`)
  raised permission prompts in the lead's terminal, and the author answered **No** to each.
  migrator-b ran `cat`, `npm run lint`, and `node scripts/check-routes.js` without any prompt.
- Afterward: `npm test` 10 passed, 0 failed; no service imports `db.js`.

Tokens (input plus cached, per model request):

| Agent | Requests | Peak payload | Total input |
|---|---|---|---|
| Lead | 20 | 66,036 | 1,083,060 |
| migrator-a | 24 | 53,511 | 1,063,408 |
| migrator-b | 22 | 50,047 | 952,252 |
| migrator-c | 11 | 46,472 | 454,648 |
| **Team** | 77 | | 3,553,368 |

For comparison, a single session did the same migration with 241,637 and 302,690 input tokens
(`../2026-10-27-dispatcher/`).

`routes.txt` holds the output of `node scripts/check-routes.js` in the team's copy afterward. A trailing `timeout: the monitored command dumped core` line is Node crashing on exit on the author's machine, after the check printed its result.
