# Precedence and permission merging

Prompt for the permission sessions: `Run the command node scripts/check-routes.js and tell me how many
routes respond. Don't use any other command.` Claude Code ran with default permissions (headless, so
anything not allowed is refused).

| Sessions | Settings | Result |
|---|---|---|
| `e8model-proj`, `e8model-proj-2` | project `"model": "sonnet"` | Answered with `claude-sonnet-5-5`, both |
| `e8model-local`, `e8model-local-2` | project `"model": "sonnet"`, local `"model": "opus"` | Answered with `claude-opus-5-5`, both |
| `e8ctl-1`, `-2` | local allow `Bash(node scripts/check-routes.js*)` | Ran; all 5 routes respond, both |
| `e8merge-1`, `-2` | project deny, local allow | `Permission to use Bash with command node scripts/check-routes.js has been denied.`, both |
| `e8cli-1`, `-2` | project deny, `--allowedTools "Bash(node scripts/check-routes.js*)"` | Denied, both |

**OpenCode** (`opencode/`), with the project's `opencode.json` set to
`{"permission": {"bash": {"*": "allow", "node scripts/check-routes.js*": "deny"}}}`:

| Sessions | Added configuration | Result |
|---|---|---|
| `oc-deny-1`, `-2` | none | Refused, both |
| `oc-inline-1`, `-2` | `OPENCODE_CONFIG_CONTENT` allowing the command (loads after the project file) | Ran, both |
| `oc-custom-1`, `-2` | `OPENCODE_CONFIG` file allowing the command (loads before the project file) | Ran, both. `debug-config-custom.json` (from `opencode debug config`) shows the merged rules as `{"node scripts/check-routes.js*": "deny", "*": "allow"}`: the deny survives but `"*": "allow"` is now the last matching rule. `debug-config-project-only.json` shows the original order |
| `oc-skill-1`, `-2` | `code-review` in both `.claude/skills/` (marked `FROM-CLAUDE-DIR`) and `.opencode/skills/` (marked `FROM-OPENCODE-DIR`) | Skill call `code-review`; both reports begin `FROM-OPENCODE-DIR` |
