# A path-scoped rule across /compact

Split configuration. `<n>.step1`: `Read src/api/routes.js and tell me how many routes it defines.
One sentence.` `<n>.step2`: `/compact`, resumed. `<n>.step3`, resumed: `Without reading any file or
running anything, quote every project instruction you currently have about route handlers and about
database access, word for word where you can, and say where each came from.` `ctl-<n>` skips step 2.

| Run | After compaction, attached again | Summary copied the API rules | Answer |
|---|---|---|---|
| 1 | `CLAUDE.md` only | Yes | Quoted `CLAUDE.md` exactly; said the API rules were available only as the summary's copy |
| 2 | `CLAUDE.md` only | Yes | Same |
| ctl-1, ctl-2 | (no compaction) | (none) | Quoted both files word for word |

The compaction summary is in each `step2`/`step3` `.summary.json` under `compact_summary`.

Each step ran as a separate `claude -p --resume` process. In one continuous process (`../2026-11-03-single-process/`), Claude Code also re-read the two most recent files after compaction, and the API rule came back word for word.
