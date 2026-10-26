# The Chapter 3 task ladder

Seven tasks of increasing scope against `sample-project/`. Run the ladder two ways: once as one
continuous session, and once with a fresh session per task. Comparing the two shows what the
shared context window costs. Real runs of both, in Claude Code and OpenAI Codex, are in
`runs/2026-10-22-ladder/`.

## The rules: send these first

In a continuous session, send them as the first message. In fresh sessions, put them at the top
of every task's message.

```text
Project rules for this whole session:
1. All database access goes through the repository classes in src/repositories/. Code in src/services/ must not import query() or update() from src/db.js in anything you add or change.
2. Every new or changed function gets a test.
3. No new dependencies: package.json keeps an empty dependency list.
```

## The tasks

Each task ends with "Run npm test when you're done."

| # | Task |
|---|---|
| 1 | Add a findByEmail method to UserRepository and a test for it. |
| 2 | Make listActiveUsers in src/services/user-service.js use UserRepository. |
| 3 | Add an OrderRepository.findQuotes() method that returns orders with status "quote", and a test. |
| 4 | Migrate all of src/services/order-service.js to OrderRepository, updating its tests. |
| 5 | Add a PaymentRepository, migrate src/services/payment-service.js to it, and update its tests. |
| 6 | Add a GET /users/:id/payments endpoint with a test, using the repositories. |
| 7 | Add soft-delete filtering to every read path, add a GET /reports/active-users-count endpoint with a test, and run the full suite. |

## Set up a working copy

`score-task.sh` commits after every task, so run each ladder run in its own copy of
`sample-project/` that is its own Git repository (set `WORK` to a new folder each time), and keep
transcripts outside it (anything inside gets committed, and the next task's agent can read it):

```bash
export CH3=/path/to/graph-engineering-with-ai-agents-code/ch03-context-wall
export WORK=~/ch03-cont-1
cp -r "$CH3/../sample-project" "$WORK" && cd "$WORK"
git init -q && git add -A && git commit -qm baseline
export RUNS=~/ch03-runs/$(basename "$WORK") && mkdir -p "$RUNS"
```

## Running each task headless

Our runs used these commands. The flags let the agent edit files and run any shell command without
asking, so run them inside the sandbox from Chapter 2. Narrowing `--allowedTools` to patterns such
as `Bash(npm test *)` isn't a substitute, since `npm test` runs files the agent can edit. Our runs
also had the author's own skills and MCP servers loaded; a clean setup gives a lower baseline.

- Claude Code: `claude -p "<task>" --permission-mode acceptEdits --allowedTools Bash --output-format stream-json --verbose > "$RUNS/task3.jsonl"`
  (add `--resume <session-id>` for every message after the first of a continuous session).
- OpenAI Codex: `codex exec --json --sandbox workspace-write "<task>"` (or `codex exec ... resume <thread-id> "<task>"`).
  Its `--json` output has no per-request usage, so measure the session log instead:
  `~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread-id>.jsonl`. A continuous session keeps every
  turn in one log; `measure-usage.py --turns` splits it into one line per turn.
  If your version compresses the log to `.jsonl.zst`, decompress it with `zstd -d` first.

## After each task

From the working copy:

```bash
bash "$CH3/score-task.sh" task3
python3 "$CH3/measure-usage.py" "$RUNS/task3.jsonl"
python3 "$CH3/record-curve.py" --task 3 --tokens 41301 --input 81179 --aas 3 --run continuous --csv "$RUNS/curve.csv"
```

`score-task.sh` prints AAS out of 3 (with `c1` to `c3` for the three rules) and commits the task's
changes. `measure-usage.py` prints the task's peak payload and total input, which `record-curve.py`
takes as `--tokens` and `--input`. CTS is a running sum over every row with the same `--run`, so
each run keeps its own `curve.csv` in its `$RUNS` folder. Read the diff before you record a miss: the scorer counts a
changed function that already had a test as a rule 2 miss.

## The compaction test

At the end of a continuous Claude Code session, run `/compact`, then give this task with no
reminder of the rules, and score it:

```text
Add a function totalPaidCentsByUser() to src/services/order-service.js that returns an object mapping each user id to the total cents of their paid orders, with a test. Run npm test when you're done.
```

Then give a harder probe, in a file the ladder never migrates in Claude Code, which still imports
`query` from `src/db.js`:

```text
Add a function findUserForLogin(email) to src/services/auth-service.js that returns the active (not soft-deleted) user with that email, or null if there isn't one, with a test. Run npm test when you're done.
```

Both probes can pass without the rules: a session with no rules at all built `findUserForLogin`
on `UserRepository` too. The probe that separates them asks for the file's own style, which pulls
toward `update()` from `db.js`:

```text
Add a function recordLogin(email, callback) to src/services/auth-service.js that sets last_login_at to the current time on the active user with that email, in the same callback style as the other functions in that file, with a test. Run npm test when you're done.
```

With no rules, both of our sessions imported `update` from `db.js` (rule 1 broken). To test where
the rules can live, run tasks 1 to 3 in one session, `/compact`, and give this probe, three ways:
with the rules as the first message, with the rules only in `CLAUDE.md`, and with the rules in
`docs/RULES.md` and a first message asking the agent to read and follow it. For a fresh control,
send the rules and the probe as the only message of a new session.

## The stress test

From a new working copy, run `python3 "$CH3/make-logs.py"` to write seven log files
of about 43,000 tokens each, commit them, then in one session send the rules followed by these
seven requests (N from 1 to 7), and finally the `recordLogin` probe from the compaction test:

```text
Use your file-reading tool, not grep or other shell commands, to read all of logs/log-N.txt into the conversation. Then tell me the timestamp of the third line that contains ERROR. Report the timestamp only.
```

The correct answers are listed in `runs/2026-10-22-stress/README.md`.
