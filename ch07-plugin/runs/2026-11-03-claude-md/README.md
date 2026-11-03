# Conflicting CLAUDE.md files

Claude Code 2.1.316, `claude-opus-5-5`, headless with `--setting-sources project,local
--permission-mode acceptEdits --allowedTools "Bash(npm test*)" "Bash(node --test*)"`, two sessions per
setting, on fresh committed copies of `sample-project/` placed in a `project/` folder so a CLAUDE.md
could sit in the folder above it.

Each instruction file said `Every new file starts with the comment line // Owner: <team>.` The task:
`Create src/services/health-service.js exporting a function ping(callback) that calls back with null
and 'ok', and a test for it in tests/health-service.test.js. Run npm test when you're done.`

| Sessions | Instruction files | First line of the service file | First line of the test file |
|---|---|---|---|
| `ctl-1`, `-2` | `project/CLAUDE.md`: orders-team | orders-team, both | orders-team, both |
| `parent-1`, `-2` | `CLAUDE.md` in the folder above: platform-team; `project/CLAUDE.md`: orders-team | orders-team, both | orders-team, both |
| `local-1`, `-2` | `project/CLAUDE.md`: orders-team; `project/CLAUDE.local.md`: alex-sandbox | alex-sandbox, both | alex-sandbox, both |
| `rule-1`, `-2` | `project/CLAUDE.md`: orders-team; `project/.claude/rules/services.md` with `paths: ["src/services/**"]`: payments-team | payments-team, both | orders-team, both |

Every session's final reply named both files and said why it chose one: the project file is "closer to
the code", the local file is "the more specific instruction" (both local sessions offered to switch
to orders-team if the files would be committed), and the path rule covers `src/services/` only.

A user-level `~/.claude/CLAUDE.md` loads in the same position as the parent-folder file, before the
project's; it wasn't used here because a throwaway `CLAUDE_CONFIG_DIR` has no sign-in.
