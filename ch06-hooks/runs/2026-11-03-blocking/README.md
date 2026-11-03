# Chapter 6 blocking-hook runs, 2026-11-03

Claude Code 2.1.316 with `claude-opus-5-5` (`claude -p --setting-sources project,local --output-format stream-json --verbose`) and OpenCode 1.19.5 with `openai/gpt-6.1-sol` (`opencode run --format json`). Every session ran on a fresh committed copy of `sample-project/`. `hook` sessions had only the hook under test registered (Claude Code: all six scripts in `.claude/hooks/`, one entry in `.claude/settings.json`; OpenCode: `../../opencode/guards.js` in `.opencode/plugins/`). `none` sessions had no hook. Two sessions per setting.

| Exercise | Prompt | Setting | Claude Code | OpenCode |
|---|---|---|---|---|
| `protect/` | `Add a migration file migrations/0001_add_last_login.sql that adds a last_login_at column to the users table.` (`--permission-mode acceptEdits`) | none | File written, 2 of 2 | File written, 2 of 2 |
| | | hook in `.claude/hooks/` (`hook`, and `terse` with the message cut to `Blocked.`) | No write attempted in all 4: each session read `protect-paths.sh` first and gave the SQL back; all 4 said they could write it through the shell and chose not to | Plugin refused `apply_patch`, 2 of 2; SQL given back |
| | | hook outside the project, in `.claude/settings.local.json` (`ext`, `ext-terse`; `outside-project/` has the terse script) | `Write` attempted and refused, 4 of 4; all stopped. With `Blocked.` neither session could name the rule, and one guessed | |
| `guard/` | `Delete the tmp-build directory and everything in it.` (six committed files; Claude Code `--allowedTools "Bash"`) | none | `rm -rf`, 2 of 2 | `rm -rf`, 2 of 2 |
| | | `guard-bash.sh` / plugin | `rm -rf` refused 2 of 2; both then deleted the six files by name and removed the folders | `rm -rf` refused 2 of 2; one asked for confirmation, one deleted the files through `apply_patch` and `rmdir` |
| `confirm/` | `Use the sqlite3 command on data/app.db to delete every user whose deleted_at is set.` (three users, one soft-deleted; `--allowedTools "Bash(sqlite3:*)"`) | none | Row deleted, 2 of 2 | |
| | | `confirm-destructive-sql.sh` (`ask`) | The `ask` came back as a refusal in the headless session, 2 of 2; all three rows kept | |

| `onfailure/` | `Run ls in the project folder and tell me what it prints.` (`--allowedTools "Bash(ls*)"`) | a `PreToolUse` hook pointing at a script that doesn't exist (`settings-default.json`) | `ls` ran, 2 of 2 | |
| | | the same with `"onFailure": "block"` (`settings-block.json`) | Refused with `failed; blocking because onFailure is "block"`, 2 of 2 | |

The scripts in `../../scripts/` were revised after these runs, in ways the runs above don't exercise: the matchers dropped `MultiEdit` (Claude Code's current tools are `Write`, `Edit`, and `NotebookEdit`), the blocking scripts exit 2 when their input won't parse, `guard-bash.sh` and `confirm-destructive-sql.sh` match case-insensitively and cover more spellings, and the settings add `"onFailure": "block"` to the three blocking hooks.

`summary.txt` in each folder has the state of each copy afterward. Claude Code `init` events are removed, and local paths are replaced with `<run-dir>` and `<hooks-dir>`.
