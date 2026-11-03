# Compaction inside one process

The compaction tests in `../2026-11-03-compaction/` and `../2026-11-03-skill-compaction/` ran each step
as a separate `claude -p --resume` process. These runs send all three messages to one process
(`claude -p --input-format stream-json --output-format stream-json --verbose`), so the compaction
happens inside a continuous session. `<run>.loaded.txt` is `../../loaded-context.py` on the session.

| Run | Step 1 | After `/compact` | Answer to the probe |
|---|---|---|---|
| `rule-1`, `rule-2` | Read `src/api/routes.js` (split configuration; API rule loaded) | `CLAUDE.md` attached again; Claude Code re-read the two most recent files, `.claude/rules/api-conventions.md` and `src/api/routes.js` | Quoted the API rules and `CLAUDE.md` exactly |
| `skill-1`, `skill-2` | Skill tool loads the 9,000-token `release-checklist` | The skill re-attached as an `invoked_skills` entry of 20,000 characters, cut off partway through item 124 | Quoted the FIRST RULE exactly; the LAST RULE was in the part cut off |

Payloads: rule runs 31,872 and 32,680 before compaction, 34,137 after (31,870, 32,678, 34,347);
skill runs 31,478 and 40,056 before, 39,074 after (31,475, 40,053, 39,057). In the resumed-process
runs, the payload after compaction grew only by the summary.
