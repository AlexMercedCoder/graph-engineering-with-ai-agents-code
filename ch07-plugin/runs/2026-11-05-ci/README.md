# CI checks and install timing

Claude Code 2.1.316, 2026-11-05, no model sessions.

`ci/check-install.sh` on the companion's plugin:

```text
ok   Skills: 4
ok   Agents: 3
ok   Hooks: 5
```

Exit 0, 5.5 seconds wall time. (Rerun after the final Chapter 6 sync, which added `git-context.sh` on `UserPromptSubmit` and `audit.sh` on `PostToolUseFailure`, so five hook events.) On a copy of `ch07-plugin` with `team-workflow/skills/` moved to
`team-workflow/.claude-plugin/skills/`:

```text
FAIL Skills: loaded 0, plugin ships 4
ok   Agents: 3
ok   Hooks: 5
```

Exit 1 (`claude plugin validate --strict` passed that copy).

`ci/check-version-bump.sh HEAD team-workflow` in a scratch repository holding `team-workflow` 1.0.0:

| Working tree | Output | Exit |
|---|---|---|
| `protect-paths.sh` changed, version 1.0.0 | `FAIL team-workflow changed since HEAD but version is still 1.0.0` | 1 |
| same change, version 1.0.1 | `ok   team-workflow version 1.0.0 -> 1.0.1` | 0 |
| no change | `ok   no changes in team-workflow` | 0 |

Install timing: `claude plugin marketplace add <ch07-plugin> --scope project` followed by
`claude plugin install team-workflow@book-platform --scope project`, each run in a fresh
configuration directory and a fresh copy of `sample-project/`: 2.46, 1.66, and 3.64 seconds.
