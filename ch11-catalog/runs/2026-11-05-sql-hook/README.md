# The SQL hook, November 5, 2026

Claude Code 2.1.316 with `claude-opus-5-5`, the raw setup plus `hooks/validate-sql.py` as a
`PreToolUse` hook on Bash (`bash eval/run-agents.sh claude rawhook <out>`), two sessions.
Transcripts are sanitized: the run folder is `<run-dir>`, the companion path `<companion>`, and the
session's init and rate-limit events are removed.

| Session | Score | Commission (q6) | Gross written premium (q2) | Input tokens |
|---|---|---|---|---|
| claude-rawhook-1 | 5/6 | refused after the hook blocked `fct_commissions` | wrong (`premium_amt_gross`) | 308,596 |
| claude-rawhook-2 | 6/6 | refused after the hook blocked `fct_commissions` | correct | 410,600 |

Session 2 followed the hook's path in its error message, read `hooks/validate-sql.py`,
`validate.py`, and `catalog.yaml`, and answered from the catalog's definitions. Without the hook
(`../2026-11-03-governed-access/`), both Claude Code raw sessions scored 4/6 and reported the
commission total.

`replay.txt` replays every `sqlite3` command from the four November 3 raw sessions through the hook
(`python3 eval/replay_hook.py`). It would have blocked the commission queries in all four, and the
wrong-premium queries in the two OpenCode sessions, which labeled the column
`gross_written_premium`; the Claude Code sessions labeled it `gwp` and would have passed.

Two earlier attempts were discarded. The first registered the hook with an unexpanded path, so
every command failed with a hook error. The second ran before two validator fixes found by the
replay: a select-list expression containing a comma, such as `ROUND(SUM(x), 2) AS metric`, was
skipped by the lineage check, and names defined in a `WITH` clause were reported as unknown tables.
Both cases are now in `eval/check_hook.py`.
