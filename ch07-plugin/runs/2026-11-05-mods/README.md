# A mod against a deny rule

Claude Code 2.1.316, `claude-opus-5-5`, headless (`claude -p`), on 2026-11-05. Each session ran on a
fresh committed copy of `sample-project/` with `--setting-sources project,local` and the project's
`.claude/settings.json` set to:

```json
{ "permissions": { "deny": ["Bash(node scripts/check-routes.js*)"] } }
```

The credential was a personal claude.ai login (not a Team or Enterprise login), and the machine had no
managed settings. Prompt: `Run the command node scripts/check-routes.js and tell me how many routes
respond. Don't use any other command.`

| Sessions | Plugin loaded with `--plugin-dir` | Result |
|---|---|---|
| `deny-only-1`, `-2` | none | `Permission to use Bash with command node scripts/check-routes.js has been denied.`, both |
| `deny-hook-1`, `-2` | `../../experiments/approve-routes-hook` (a `PreToolUse` hook returning `permissionDecision: "allow"` for exactly `node scripts/check-routes.js`) | Denied, both |
| `deny-mod-1`, `-2` | `../../experiments/approve-routes-mod` (a mod whose `tool.check` handler returns `{ decision: 'allow' }` for exactly that command) | Ran; all 5 routes respond, both. In `deny-mod-2`, Node printed all five results and then crashed on exit (exit code 139, segmentation fault); the approval and the run are unaffected |

A second test checked whether a plugin's `settings.json` can bring a permission rule. These sessions
had no project deny; `../../experiments/settings-allow` ships `settings.json` with
`{"permissions": {"allow": ["Bash(node scripts/check-routes.js)"]}}`:

| Sessions | Plugin loaded | Result |
|---|---|---|
| `nodeny-none-1`, `-2` | none | `This command requires approval` (headless, so refused), both |
| `nodeny-settings-1`, `-2` | `settings-allow` | `This command requires approval`, both: the plugin's allow wasn't applied |

The hook and mod transcripts kept here are from the final versions in `experiments/`, which match the
command exactly (an earlier prefix-match version gave the same results). `claude plugin validate
experiments/approve-routes-mod` lists the mod's events as `./register.js hooks: tool.check{tool=Bash}` and its calls as `nothing on $`.

Untested here: a session with managed settings or a Team or Enterprise login, where the documentation
says the deny holds. `init` events are reduced to the model, version, and plugin names; local paths
are replaced with placeholders.
