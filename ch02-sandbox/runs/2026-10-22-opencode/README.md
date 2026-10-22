# Chapter 2 verification exercise in OpenCode, 2026-10-22

OpenCode 1.19.0 with the `openai/gpt-6.1-sol` model, non-interactive (`opencode run`, resumed
per request), using the chapter's `opencode.json` (`opencode-chapter.json`). Each run copies the
companion repository's layout: the Git root sits one level above `sample-project/`, and OpenCode
starts inside `sample-project/`, with `opencode.json` there.

| Request | `oc-1`, `oc-2` (chapter config) |
|---|---|
| 1. Add a line to `tests/scratch.txt` | Allowed (the patch tool reports the path as `sample-project/tests/scratch.txt`) |
| 2. Add a line to the migration | Refused: the patch tool returned "The user has specified a rule which prevents you from using this specific tool call." |
| 3. `echo edited >> migrations/0001_dummy.sql` | Refused: no shell tool was offered (`"*": "deny"`); the model declined |
| 4. Show `.env` | Refused: the read tool returned the same rule error |
| 5. Fetch a web page from the shell | Refused: "I don't have a shell tool available in this session" |
| `git status` afterward | only `sample-project/tests/scratch.txt` |

Both sessions passed all six steps.

`oc-old` checks the edit patterns the chapter used before its technical review, `src/*` and
`tests/*` (`opencode-old-patterns.json`), with step 1 only. OpenCode refused the scratch-file
edit, because it matches edit paths from the Git root, where the path is
`sample-project/tests/scratch.txt`.

Files per run: `step*.jsonl` (event streams, local paths replaced), `git-status.txt`,
`changes.diff`, `migration-after.sql`.
