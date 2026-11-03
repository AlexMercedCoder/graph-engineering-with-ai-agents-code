# Chapter 6: Overcoming Non-Deterministic Flow

| Path | What it is |
|---|---|
| `scripts/protect-paths.sh` | `PreToolUse`: refuses `Write` and `Edit` under `migrations/`, `.env`, `package-lock.json`, and `terraform/` |
| `scripts/guard-bash.sh` | `PreToolUse` on `Bash`: refuses recursive deletes (`rm -rf`, `rm -fr`, `rm -r -f`), `git push`, `git reset --hard`, `chmod 777`, and downloads piped to a shell, case-insensitively. Misses `find -delete`, deletion through the file tools, and commands hidden in scripts |
| `scripts/confirm-destructive-sql.sh` | `PreToolUse` on `Bash`: returns `ask` for `DROP TABLE`, `TRUNCATE`, and `DELETE FROM`, in any case |
| `scripts/lint-on-edit.sh` | `PostToolUse`: formats the edited file, and exits 2 with a message when a file under `src/services/` still imports from `src/db.js` |
| `scripts/test-on-stop.sh` | `Stop`: runs `npm test` when `src/` or `tests/` changed, and blocks the stop on failure; on the third failure in a row it lets the agent stop and resets |
| `scripts/audit.sh` | `PreToolUse` and `PostToolUse` on `*`: appends one JSON line per event to `.agent-work/audit.jsonl` |
| `settings.json` | Claude Code settings that register all six, with `"onFailure": "block"` on the three blocking hooks (Claude Code 2.1.295 or later) |
| `opencode/guards.js` | OpenCode plugin with the protect, guard, lint, and audit behavior (handles `write`, `edit`, and `apply_patch`) |
| `runs/` | Real runs from 2026-11-03: `2026-11-03-blocking/` and `2026-11-03-edges/` |

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

An agent that can read `.claude/hooks/` may follow a hook without ever triggering it. To watch a hook fire, keep the script outside the project and register it with an absolute path in `.claude/settings.local.json`, as the `ext` runs did.

Test any hook by hand before trusting it:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"migrations/1.sql"}}' | .claude/hooks/protect-paths.sh; echo "exit $?"
```

Hooks declared in a project subagent's definition (`.claude/agents/*.md`) are skipped until the folder is trusted, and a `claude -p` session doesn't count as trusted. Agents in `~/.claude/agents/` or passed with `--agents` don't need that step; `runs/2026-11-03-edges/scoped-agents/agents.json` shows the `--agents` form. Subagents shipped inside a plugin ignore the `hooks` field entirely, so a plugin's hooks belong in its own hooks file.
