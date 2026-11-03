# Chapter 7: Managing Configuration Collision

| Path | What it is |
|---|---|
| `team-workflow/` | The plugin: the Chapter 4 skills, the Chapter 5 agents, and the Chapter 6 hook scripts, with `hooks/hooks.json` generated from `ch06-hooks/settings.json` |
| `release-tools/` | A second plugin, version 1.1.0: a `write-migration` skill that drafts into `migration-drafts/` and a `code-review` skill for releases |
| `release-tools-1.0.0/` | The version that collides with `team-workflow`: its `write-migration` writes into `migrations/`, which `protect-paths.sh` refuses. Not in the marketplace; load it with `--plugin-dir` to reproduce the collision |
| `.claude-plugin/marketplace.json` | The `book-platform` marketplace, listing both plugins by relative path |
| `tools/sync-from-chapters.sh` | Rebuilds `team-workflow` from `ch04-routing/skills`, `ch05-subagents/agents`, and `ch06-hooks`; run it after changing any of them |
| `runs/` | Real runs from 2026-11-03; each folder has a README |

## Try it without installing

```bash
claude plugin validate ./team-workflow
claude --plugin-dir ./team-workflow                       # one session, nothing installed
claude --plugin-dir ./team-workflow --plugin-dir ./release-tools-1.0.0   # the collision
claude --plugin-dir ./team-workflow --plugin-dir ./release-tools         # the 1.1.0 fix
```

In a session, `/team-workflow:code-review src/services/payment-service.js` runs the plugin's review.
`/code-review` runs Claude Code's built-in skill of the same short name.

## Install it in a throwaway configuration

```bash
export CLAUDE_CONFIG_DIR=$(mktemp -d)      # keeps your real settings and plugins untouched
cd <a fresh copy of sample-project>
claude plugin marketplace add <path to ch07-plugin> --scope project
claude plugin install team-workflow@book-platform --scope project
claude plugin details team-workflow       # 4 skills, 3 agents, 3 hook events
```

The configuration directory isn't signed in, which doesn't matter for installing, validating, and
updating. A plugin enabled in a project's `.claude/settings.json` loads only after the workspace
trust dialog, and a headless `-p` session doesn't accept it, so use `--plugin-dir` for scripted
sessions.

## The hooks file

`team-workflow/hooks/hooks.json` registers the six Chapter 6 scripts on the same events and matchers
as `ch06-hooks/settings.json`, with each command written as
`"${CLAUDE_PLUGIN_ROOT}"/hooks/scripts/<script>.sh` and `"onFailure": "block"` on the three blocking
hooks (Claude Code 2.1.295 or later). The scripts are byte-for-byte copies of `ch06-hooks/scripts/`.
