# Chapter 2: Hardening the Agent Sandbox

The configuration and the verification exercise from Chapter 2. The five
harnesses do not share a configuration format, so each section below is the
starting point for one harness. None of them is equivalent to another; run the
verification exercise after applying yours. Check every setting against the
documentation for the version you have installed.

Work on a throwaway branch:

```bash
git switch main
git switch -c ch02-sandbox
```

## Claude Code: `.claude/settings.json`

```json
{
  "permissions": {
    "deny": [
      "Edit(/migrations/**)",
      "Read(/.env)"
    ]
  }
}
```

Run `/permissions` to see the loaded rules. These rules also cover common shell
file commands such as `cat` and redirection, but not a script that opens files
itself. Enable Claude Code's sandbox to block every process.

## OpenAI Codex

```bash
codex --sandbox read-only --ask-for-approval never
codex --sandbox workspace-write --ask-for-approval never
```

Configuration lives in TOML (`~/.codex/config.toml`). `workspace-write` allows
writes across the whole workspace, not only `src/` and `tests/`.

## OpenCode: `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "deny",
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "edit": {
      "*": "deny",
      "src/*": "allow",
      "tests/*": "allow"
    }
  }
}
```

Shell stays denied. Check agent-specific overrides: the last matching rule wins.

## Google Antigravity and Pi

Neither is configured by a file in this folder. For Antigravity, require review
for terminal commands and enable the terminal sandbox in its security settings;
the CLI keeps permissions in `~/.gemini/antigravity-cli/settings.json`. For Pi,
select only reading and search tools, check active extensions, and run it inside
a container or separate user account before allowing writes or shell access.

## Verification exercise

Create and commit the dummy files yourself, outside the agent:

```bash
cd sample-project
mkdir -p migrations
echo "-- dummy migration: this file must not change" > migrations/0001_dummy.sql
echo "API_TOKEN=not-a-real-secret" > .env
echo "scratch file the agent may edit" > tests/scratch.txt
git add -A && git commit -m "Chapter 2 sandbox fixtures"
```

Then ask the agent, one request at a time, to:

1. Add `edited by agent` to `tests/scratch.txt` (should succeed).
2. Add the same line to `migrations/0001_dummy.sql` (should be refused by the
   harness, not merely declined by the model).
3. If the shell is enabled, run `echo edited >> migrations/0001_dummy.sql`
   (should be refused).
4. Show the contents of `.env` (should be refused).
5. If no network access is allowed, fetch a public web page with a shell
   command (should be blocked).
6. Afterward, run `git status --short` yourself: only `tests/scratch.txt`
   should be modified.

Record each result as allowed, refused, or untested, with the harness version
and active settings.

## Project instructions: `CLAUDE.md` or `AGENTS.md`

This file is advisory. The runtime settings above do the enforcing.

```markdown
# Order-management API

This project uses JavaScript modules and has no runtime dependencies.
Run tests with `npm test`, which uses Node's built-in test runner.

## Architecture

Database access belongs in src/repositories/. Code in src/services/
calls those repository classes and never imports query() or update()
from src/db.js. Handle errors at asynchronous boundaries, and test
failure cases as well as successful requests.

Keep runtime dependencies empty unless the task explicitly authorizes
adding one. Add tests for new behavior and explain any changed test
expectations.

## Working on a task

Change the source and tests needed for the current feature. Leave
unrelated refactors and dependency updates for separate work.
After a source change, run `npm test` before reporting completion.
If a check cannot run, report that limitation with the result.

The exercise keeps migrations, secret files, and lock files outside
the permitted edit scope. Those restrictions are enforced by runtime
settings; this file documents the intended policy.
```
