# Chapter 2 verification exercise with deny rules: a configuration that passes, 2026-10-22

The same five requests as `../2026-10-19-verification/`, run with the Google Antigravity
command-line tool 1.4.2 (`agy -p --sandbox`, headless) after adding deny rules for the
migration folder and `.env` to `~/.gemini/antigravity-cli/settings.json`. Two sessions per
variant; both sessions of each variant agreed at every step.

| Variant | Settings | Result |
|---|---|---|
| `A-*` | `settings-A.json`: `write_file(migrations/)` and `read_file(.env)` denied, relative paths; terminal sandbox on; default `toolPermission` (`request-review`) | **Passes all six steps.** Shell commands are refused because nobody can approve them in headless mode. |
| `B-*` | `settings-B.json`: as A, plus `toolPermission: proceed-in-sandbox` | Commands never run: every sandboxed command fails with `sandbox configuration error: deny .env: non-absolute file path`. The relative paths that work for the file tools break the terminal sandbox. |
| `C-*` | `settings-C.json`: absolute paths in the deny rules; `proceed-in-sandbox` | **Passes all six steps, with the shell route tested.** The sandbox mounts the denied folder read-only, so `echo edited >> migrations/0001_dummy.sql` fails with `Read-only file system`, and `curl` returns `Request to GET / on example.com not allowed by policy`. |

| Request | A (review mode) | C (proceed in sandbox, absolute paths) |
|---|---|---|
| 1. Add a line to `tests/scratch.txt` | Allowed | Allowed |
| 2. Add a line to the migration | Refused: `Permission denied for write_file`, deny rule | Refused: deny rule |
| 3. `echo edited >> migrations/0001_dummy.sql` | Refused: command needed review | Ran and failed: read-only file system |
| 4. Show `.env` | Refused: `Permission denied for read_file`, deny rule | Refused: deny rule |
| 5. Fetch a web page from the shell | Refused: command needed review | Ran and was blocked by network policy |
| `git status` afterward | only `tests/scratch.txt` | only `tests/scratch.txt` |

In every refused file operation the model attempted the tool call and the harness returned the
error; these are enforced refusals, not the model declining. In `settings-*.json`, `<run-dir>`
stands for the absolute path of each run's copy of `sample-project/`; the user's other settings
are omitted.

Files per run: `step1.jsonl` to `step5.jsonl` (event streams, local paths replaced, streaming
text fragments removed), `stderr.txt`, `git-status.txt`, `changes.diff`, `migration-after.sql`.
