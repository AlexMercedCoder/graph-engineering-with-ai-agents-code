# Chapter 3 compaction tests: real runs, 2026-10-22

Claude Code 2.1.308 (`claude-opus-5-5`, `claude -p` with `--permission-mode acceptEdits
--allowedTools Bash`), two runs per setup, each in its own copy of `sample-project/`. The probes
are in `../../task-ladder.md`.

## Do the probes need the rules?

A probe only tests rule-keeping if a session without the rules would break one.

| Runs | Setup | Probe | AAS |
|---|---|---|---|
| `cc-norule-1`, `cc-norule-2` | No rules anywhere | `findUserForLogin` | 3 of 3 in both: one built it on `UserRepository`, the other reused the file's own `findByEmail` |
| `cc-norule3-1`, `cc-norule3-2` | No rules anywhere | `recordLogin`, "in the same callback style" | 2 of 3 in both: `import { query, update } from '../db.js'` |

So `findUserForLogin` (and the ladder's `totalPaidCentsByUser` probe) can't show whether the rules
survived, and `recordLogin` can.

## Where the rules can live

Each session sent its first message, ran ladder tasks 1 to 3, ran `/compact`, and took the
`recordLogin` probe with no reminder.

| Runs | Where the rules were | Compaction (tokens) | Probe AAS |
|---|---|---|---|
| `p3-msg-1`, `p3-msg-2` | First message of the session | 41,615 to 13,963; 40,088 to 13,854 | 3 of 3 in both |
| `p3-md-1`, `p3-md-2` | `CLAUDE.md` only (`CLAUDE.md` in this folder) | 41,262 to 14,115; 41,436 to 13,979 | 3 of 3 in both |
| `p3-rf-1`, `p3-rf-2` | `docs/RULES.md`, which the first message asked the agent to read and follow | 42,347 to 14,094; 39,539 to 13,929 | 3 of 3 in both |
| `p3-fresh-1`, `p3-fresh-2` | Rules and probe as the only message, no compaction | none | 3 of 3 in both |

Every passing session added a method to `UserRepository` and called it from `recordLogin`, in
callback style, without importing from `db.js`. Every compaction summary
(`compaction-summary.txt`, exported from Claude Code's session transcript) copied the three rules
word for word under its first heading, **Primary Request and Intent**, whichever way the rules
had arrived.

## Earlier variants, with the `findUserForLogin` probe

| Runs | Setup | Compaction (tokens) | Probe AAS |
|---|---|---|---|
| `cc-md-1`, `cc-md-2` | Rules in `CLAUDE.md` only; tasks 1 to 3 | 44,903 to 14,620; 39,801 to 13,797 | 3 of 3 in both |
| `cc-readrule-1`, `cc-readrule-2` | Rules in `docs/RULES.md`, read on request; tasks 1 to 3 | 40,499 to 13,956; 40,856 to 13,720 | 3 of 3 in both |
| `cc-p2fresh-1`, `cc-p2fresh-2` | Rules and probe as the only message | none | 3 of 3 in both |

These passed, but so did the no-rules control, so they don't count as evidence that the rules
survived. The continuous ladder sessions took the same probe after their `/compact`
(`../2026-10-22-ladder/cc-cont-*/probe2.jsonl`).

Several `scores.txt` files show task 2 at 2 of 3: the agent changed `listActiveUsers`, which
already had a test, without adding one. That is the scorer's known rule 2 case, not a broken rule.

Files: `stream-json` output per step, minus `init` events and thinking-token counters,
`scores.txt`, and `changes.diff`. Local paths are replaced with placeholders.
