# Chapter 6: Overcoming Non-Deterministic Flow

| Path | What it is |
|---|---|
| `scripts/protect-paths.sh` | `PreToolUse`: refuses `Write` and `Edit` to a `migrations/` or `terraform/` folder anywhere in the path below the project folder (it strips `$CLAUDE_PROJECT_DIR`, or the event's `cwd`, first), and to files named `.env`, `.env.*`, or `package-lock.json`. Matches whole path segments, so `old-migrations/` and `.envrc` pass |
| `scripts/guard-bash.sh` | `PreToolUse` on `Bash`: refuses recursive deletes (`rm -rf`, `rm -fr`, `rm -r -f`), `git push`, `git reset --hard`, `chmod 777`, and downloads piped to a shell, case-insensitively. Misses `find -delete`, deletion through the file tools, and commands hidden in scripts |
| `scripts/confirm-destructive-sql.sh` | `PreToolUse` on `Bash`: returns `ask` for `DROP TABLE`, `TRUNCATE`, and `DELETE FROM`, in any case |
| `scripts/lint-on-edit.sh` | `PostToolUse`: formats the edited file, and exits 2 with a message when a file under `src/services/` still imports from `src/db.js` |
| `scripts/test-on-stop.sh` | `Stop`: runs `npm test` when `src/` or `tests/` changed, and blocks the stop on failure; on the third failure in a row it lets the agent stop and resets. When the tests pass after it sent the agent back, it lists the assertion lines changed since then in a `systemMessage` and in `.agent-work/assertion-changes.log` |
| `scripts/audit.sh` | `PreToolUse`, `PostToolUse`, and `PostToolUseFailure` on `*`: appends one JSON line per event, with the tool call's ID, to `.agent-work/audit.jsonl`, masking bearer tokens, `password=`/`token=`/`secret=`/`api_key=` values and flags, credentials in URLs and after `-u`/`--user`, and `sk-`, `ghp_`, `AKIA`, and `xox` keys. Known gap: a password glued to `-p` (`mysql -ppw`) |
| `scripts/git-context.sh` | `UserPromptSubmit`: prints the branch and up to ten uncommitted files, which Claude Code adds to the model's context at every prompt |
| `tests/commands.txt`, `tests/paths.txt`, `tests/secrets.txt` | Space-separated cases: commands and paths the guards must block or allow (plus known gaps and false positives; `<project>` stands for a project folder under `/work/terraform/`), and secrets the audit log must mask (plus a listed gap) |
| `tests/check-guards.sh` | Runs every case through the shell scripts and through `opencode/guards.js` (`tests/check-plugin.mjs`); `verify.sh` runs it |
| `settings.json` | Claude Code settings that register all seven, with `"onFailure": "block"` on the three blocking hooks (Claude Code 2.1.295 or later) |
| `opencode/guards.js` | OpenCode plugin with the protect, guard, lint, and audit behavior (handles `write`, `edit`, and `apply_patch`), with the same segment matching and redaction. Its log uses the same event names and fields, except that `agent` is `null` and there is no failure event |
| `runs/` | Real runs: `2026-11-03-blocking/`, `2026-11-03-edges/`, and `2026-11-05-review/` (context hook, prompt handler, plugin placement, assertion check, audit IDs, latency) |

Add `.agent-work/` to the project's `.gitignore` before the first run: it holds the audit log, which can still contain secrets the masking doesn't recognize.

The three blocking scripts exit 2 when `jq` is missing or their input won't parse, so a failure stops the call instead of disabling the rule. The other three skip themselves.

Install everything in a copy of `sample-project/`:

```bash
mkdir -p .claude/hooks
cp "$CH6"/scripts/*.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
cp "$CH6"/settings.json .claude/settings.json
```

For OpenCode: `mkdir -p .opencode/plugins && cp "$CH6"/opencode/guards.js .opencode/plugins/`.

Each chapter exercise registers one hook at a time. For example, the lint exercise uses only:

```json
{"hooks": {"PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/lint-on-edit.sh", "timeout": 30}]}]}}
```

and the stop exercise only `{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/test-on-stop.sh", "timeout": 120}]}]}}`.

Query the audit log with `jq`:

```bash
jq -s -c 'group_by(.id)[] | {agent: .[0].agent, tool: .[0].tool, target: .[0].target, outcome: (map(.event) | if index("PostToolUseFailure") then "failed" elif index("PostToolUse") then "ran" else "refused" end)} | select(.outcome != "ran")' .agent-work/audit.jsonl   # refused or failed calls
jq -r 'select(.event == "PostToolUse" and (.tool == "Write" or .tool == "Edit")) | .target' .agent-work/audit.jsonl | sort -u   # files written or edited
jq -r 'select(.event == "PreToolUse" and .tool == "Bash") | "\(.agent)\t\(.target)"' .agent-work/audit.jsonl   # shell commands by agent
```

Test the guards after any pattern change: `tests/check-guards.sh`.

An agent that can read `.claude/hooks/` may follow a hook without ever triggering it. To watch a hook fire, keep the script outside the project and register it with an absolute path in `.claude/settings.local.json`, as the `ext` runs did. For a team, ship the blocking hooks in a plugin (Chapter 7's `team-workflow`), which lives outside the project: in `runs/2026-11-05-review/placement/` the hook fired in 2 of 2 sessions.

Test any hook by hand before trusting it:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"migrations/1.sql"}}' | .claude/hooks/protect-paths.sh; echo "exit $?"
```

Hooks declared in a project subagent's definition (`.claude/agents/*.md`) are skipped until the folder is trusted, and a `claude -p` session doesn't count as trusted. Agents in `~/.claude/agents/` or passed with `--agents` don't need that step; `runs/2026-11-03-edges/scoped-agents/agents.json` shows the `--agents` form. Subagents shipped inside a plugin ignore the `hooks` field entirely, so a plugin's hooks belong in its own hooks file.
