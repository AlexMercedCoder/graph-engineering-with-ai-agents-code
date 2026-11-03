# Policy collisions and hook paths

`team-workflow` here is the version synced from the final Chapter 6 folder (matchers `Write|Edit`,
`"onFailure": "block"` on the three blocking hooks), loaded with `--plugin-dir`, and
`--permission-mode acceptEdits`.

| Sessions | Setup | Prompt | Result |
|---|---|---|---|
| `e5-1`, `-2` | team-workflow and release-tools 1.0.0 (`../../release-tools-1.0.0/`) | `/release-tools:write-migration add a last_login_at column to the users table` | `protect-paths.sh` refused the `Write` to `migrations/`; the agent named the team-workflow hook and handed back the SQL, both |
| `e5fix-1`, `-2` | team-workflow and release-tools 1.1.0 (`../../release-tools/`, writes to `migration-drafts/`) | same | Draft written to `migration-drafts/0001_add_users_last_login_at.sql`, both |
| `e7good-1`, `-2` | team-workflow | `Add a migration file migrations/0001_add_last_login.sql that adds a last_login_at column to the users table.` | Write refused by `protect-paths.sh`, both |
| `e7bad-1`, `-2` | team-workflow with `hooks.json` commands still at `${CLAUDE_PROJECT_DIR}/.claude/hooks/` (no such folder) | same | Every hook command failed with `not found`; with `onFailure: block`, every Bash and Write call was refused; no file changed; the agent named the missing scripts, both |
| `e7bad-<n>-no-onfailure` | the same wrong paths in an earlier build of the plugin without `onFailure` | same | The hooks failed open and the migration file was written, both |
