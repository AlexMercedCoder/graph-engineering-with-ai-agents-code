# Harness guide: skills, hooks, and plugins across five harnesses

The book is designed to run on any of five agentic coding harnesses. Skills,
subagents, hooks, and plugins are portable ideas with harness-specific file
names, directories, and event vocabulary. This guide maps the mechanisms from
*Graph Engineering with AI Agents* onto all five and records the version of each
harness the mapping was verified against.

## Documented as of

The table below lists the exact release this guide was checked against. These
products move quickly, so event names, file locations, and feature flags drift.
Re-verify against each harness's own documentation before relying on a detail in
production.

| Harness | Version verified | Verification date | Source |
|---|---|---|---|
| Claude Code | 2.1.231 | 2026-08-13 | Official hooks and plugins references |
| OpenAI Codex CLI | 0.147.0 | 2026-08-13 | Official hooks reference |
| Google Antigravity | agy CLI 1.1.12, Hub 2.8.0 | 2026-08-13 | Official hooks, skills, and plugin docs |
| OpenCode | 1.18.18 | 2026-08-13 | Official plugins and skills docs |
| Pi | 0.84.1 | 2026-08-13 | Official extensions docs |

## Quick map

| Harness | Skills root | Subagents root | Hooks live in | Plugins |
|---|---|---|---|---|
| Claude Code | `.claude/skills/` (project), `~/.claude/skills/` (personal) | `.claude/agents/`, `~/.claude/agents/` | `.claude/settings.json`, or a skill/subagent definition | `.claude-plugin/` with `plugin.json` |
| OpenAI Codex CLI | `.codex/` skills directory | `.codex/agents/` | `hooks.json`, or `[hooks]` in `config.toml` | plugin manifest or `hooks/hooks.json` |
| Google Antigravity | `.agents/skills/` (workspace), `~/.gemini/antigravity-cli/skills/` (global) | `.agents/` agents directory | `.agents/hooks.json`, or `~/.gemini/config/hooks.json` | `~/.gemini/antigravity-cli/plugins/` |
| OpenCode | `.opencode/skills/` (project), `~/.config/opencode/skills/` (user) | `.opencode/agents/` | A plugin module in the project | `.opencode/plugins/`, `~/.config/opencode/plugins/` |
| Pi | `.pi/skills/` (project), `~/.pi/agent/skills/` (global) | `.pi/agents/` | A TypeScript extension | `~/.pi/agent/extensions/`, `.pi/extensions/` |

## Skills

A skill is a directory with a `SKILL.md` file: YAML frontmatter declaring the
name and description, and a Markdown body holding the procedure. The format is
the Agent Skills open standard, adopted by every harness in this book. Two
fields are required, and a skill directory is portable in a way that harness
configuration is not.

The frontmatter is all the harness loads during routing, about 100 tokens per
skill. The body loads only after the skill is selected. That separation is what
keeps a large skill index cheap.

### The portable frontmatter

| Field | Status | Travels? |
|---|---|---|
| `name`, `description` | Agent Skills spec (required) | Yes |
| `license`, `compatibility`, `metadata` | Agent Skills spec (optional) | Yes |
| `allowed-tools` | Agent Skills spec (experimental) | Support varies |

### The Claude Code extensions

These fields exist in Claude Code and not in the specification. A skill using
them still runs in Claude Code, but uploading the same skill to claude.ai or
through the Skills API produces a validation error naming the unexpected key.
If a skill needs to travel, keep the frontmatter to the six specification
fields and put anything harness-specific in a wrapper the harness owns.

| Field | Meaning |
|---|---|
| `when_to_use`, `paths`, `argument-hint` | Limits automatic activation; `paths` matches a file glob |
| `disable-model-invocation`, `user-invocable` | Makes a skill user-triggered only |
| `context`, `agent`, `background`, `hooks` | `context: fork` runs the skill in its own subagent context |
| `model`, `effort`, `shell`, `disallowed-tools` | Overrides model, reasoning effort, and tool grants for the skill |

### Where skills live

Placement decides who gets the skill, and every harness uses the same
three-tier logic with a different root.

- **Personal scope**: follows you across every project. In Claude Code this is
  `~/.claude/skills/`; in OpenCode it is `~/.config/opencode/skills/`; in Pi it
  is `~/.pi/agent/skills/`.
- **Project scope**: travels with the code, so it reaches every teammate who
  clones it. In Claude Code this is `.claude/skills/`; in OpenCode `.opencode/skills/`;
  in Pi `.pi/skills/`; in Antigravity `.agents/skills/`.
- **Organization scope**: applied by enterprise-managed settings where the
  harness supports them.

Antigravity follows the same shape: workspace skills in `.agents/skills/` and
global skills under `~/.gemini/antigravity-cli/skills/`. Its frontmatter needs
only `description`; `name` is optional and defaults to the folder name if
absent.

### If your harness does not support skills

The substitute is a `docs/procedures/` directory and one line in the project
configuration telling the agent which file to read for which job. That
reproduces progressive disclosure by hand at about 60 standing tokens. What you
give up is the routing decision, which moves from the agent to you.

## Subagents

A subagent is a Markdown file with YAML frontmatter, placed in the harness's
agents directory. In Claude Code that is `.claude/agents/` for project scope or
`~/.claude/agents/` for personal scope, with the same three-tier logic as
skills. The other harnesses use their own agents roots with the same shape.

A subagent runs in its own context window with its own tool grant. It is how a
node gets isolation: a worker receives a self-contained assignment and returns
a self-contained result, so its working material never piles up in your
session. The three coordination patterns from Chapter 5 are dispatcher,
pipeline, and fan-out and fan-in, separated by one question: do the workers
need each other's results? No means dispatcher, yes in a fixed order means
pipeline, and yes all at once at the end means fan-out.

The definitions in `ch05-subagents/agents/` and `ch05-subagents/nodes/` use the
open format and move to any harness's agents directory. `run-graph.sh` runs the
same graph as a plain shell script for a harness that cannot spawn workers.

## Hooks

Three of the five harnesses run shell commands declared in a configuration
file. The other two reach the same guarantee from in-process TypeScript. The
guarantee is identical; the file differs.

| Harness | Where a hook lives | How it is written | Event vocabulary | How it refuses |
|---|---|---|---|---|
| Claude Code | `.claude/settings.json`, `~/.claude/settings.json`, or a skill/subagent definition | Shell command (or HTTP, MCP tool, prompt, or agent handler), event JSON on stdin | The widest catalogue: `PreToolUse`, `PostToolUse`, `PermissionRequest`, `SubagentStop`, `Stop`, and two dozen more | Exit code 2, or JSON `permissionDecision` |
| OpenAI Codex CLI | `hooks.json` or `[hooks]` in `config.toml`, at `~/.codex/` or `<repo>/.codex/` | Shell command with a `matcher` | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `UserPromptSubmit`, `SubagentStop`, `Stop`, and session events | Exit code 2, or a JSON `decision` |
| Google Antigravity | `.agents/hooks.json` (workspace) or `~/.gemini/config/hooks.json` (global) | Shell command with a `matcher` | `PreToolUse`, `PreInvocation`, `PostInvocation`, plus `PostToolUse` and `Stop` | JSON `decision` with `allow`, `deny`, or `force_ask` |
| OpenCode | A plugin module in `.opencode/plugins/` | TypeScript or JavaScript function | `tool.execute.before`, `tool.execute.after`, plus session, message, and permission events | Throw from the handler |
| Pi | A TypeScript extension in `~/.pi/agent/extensions/` or `.pi/extensions/` | In-process TypeScript via `pi.on()` | Events observe; hooks intercept, including `tool_call` | Return `{ block: true }` |

Two differences change what you write. The bottom two rows are code, not
scripts: a `tool.execute.before` handler that throws on `rm -rf` is the same
guarantee as `guard-bash.sh`, expressed in the language the harness already
runs. And the refusal vocabulary is not uniform: every harness can deny, but
the exact decision values differ, and one harness has historically parsed
`ask` without acting on it. Antigravity widens the set with `force_ask`, which
forces a human prompt even in an unattended run. Where a harness cannot prompt,
fall back to `deny` with a rejection message that names the approved path.

The working hooks are in `ch06-hooks/scripts/`, and the Claude Code wiring that
registers them is in `ch06-hooks/settings.json`. `ch15-governed-workflow/`
shows the approval gate that demands a human decision in front of irreversible
tool calls.

### Enabling hooks

Hooks are on by default in Claude Code, OpenCode, Pi, and Antigravity. Codex
ships hooks behind a feature flag: set `[features] hooks = true` in
`~/.codex/config.toml` (the older `codex_hooks` key still works as a deprecated
alias). Hooks that are not enabled are silently ignored, so verify the flag
before debugging a hook that never fires.

### Verifying a hook fires

Hooks fail silently more often than they fail loudly. Work through this
sequence, because each step rules out the ones after it.

1. Confirm the harness loaded the hook at all. Claude Code's `/hooks` command
   and Codex's `/hooks` command list every active hook and the settings file it
   came from.
2. Confirm hooks are enabled. In Codex, the `[features] hooks = true` flag must
   be set or nothing runs.
3. Check the matcher against the actual tool name. Tool names are
   case-sensitive and more specific than people expect.
4. Run the script by hand with real input. Pipe a saved event JSON into it from
   the terminal and check the exit code with `echo $?`.
5. Check the exit code semantics. A hook that returns 1 instead of 2 does not
   block; it logs an error and the action proceeds.
6. Check the timeout. A hook that exceeds its timeout is terminated, and a
   terminated hook does not block.

## Plugins

A plugin bundles skills, subagents, and hooks so a colleague can install the
whole system at once. Every harness has a packaging shape, and they share the
same principle: components live at the plugin root, and a manifest marks the
bundle.

### The Claude Code plugin shape

```
team-workflow/
  .claude-plugin/
    plugin.json
  skills/     <- at the plugin root, not inside .claude-plugin/
  agents/
  hooks/
```

One structural rule causes more failed plugins than everything else combined:
only `plugin.json` goes inside `.claude-plugin/`. The `skills/`, `agents/`, and
`hooks/` directories live at the plugin root, alongside `.claude-plugin/`
rather than inside it. A plugin with `skills/` nested under `.claude-plugin/`
loads without error and without any skills, which is the worst kind of failure
because nothing reports it. Claude Code plugins can also bundle MCP servers
(`.mcp.json`), LSP servers (`.lsp.json`), and inline hooks in `plugin.json`.

Hook paths inside a Claude Code plugin use `${CLAUDE_PLUGIN_ROOT}`, not
`${CLAUDE_PROJECT_DIR}`. A plugin installs into a versioned cache directory
whose name changes on every update, so a project-relative path works on the
machine that built it and nowhere else.

### The Codex plugin shape

Codex loads plugin-bundled hooks from `hooks/hooks.json` inside the plugin root
by default, or from a `hooks` entry in `.codex-plugin/plugin.json`. Plugin hook
commands receive `PLUGIN_ROOT` and `PLUGIN_DATA` environment variables, plus
`CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility with existing
plugin hooks.

### The Antigravity plugin shape

Antigravity plugins live under `~/.gemini/antigravity-cli/plugins/<name>/` and
require a `plugin.json` marker file. Optional components sit beside it:
`mcp_config.json` for MCP servers, `hooks.json` for event hooks, plus `skills/`,
`agents/`, and `rules/` directories. An `import_manifest.json` tracks what the
agent has installed.

### Packaging steps (Claude Code, as the reference)

1. Create the plugin directory alongside the existing configuration.
2. Write the manifest at `.claude-plugin/plugin.json`. Set `version` for
   releases, or omit it to track the branch.
3. Copy the component directories (`skills/`, `agents/`) to the plugin root.
4. Move the hooks block into the plugin.
5. Validate with `claude plugin validate ./team-workflow` before publishing.
6. Delete the originals from `.claude/`. A leftover local subagent definition
   overrides the plugin's of the same name, and nothing reports why.

### Distribution with a marketplace

A marketplace is a JSON file in a Git repository that catalogs plugins and
where to fetch them. The `source` field carries the flexibility: a relative
path for a directory in the same repository, a `github` source for another
repository, or npm, zip, and Git sources with an optional SHA-256 pin for
integrity. Versioning resolves from the first of: `version` in `plugin.json`,
`version` in the marketplace entry, the Git commit SHA, the SHA-256 digest, or
`unknown`.

The worked example is `ch07-plugin/team-workflow/`. The manuscript's chapter 7
shows the full manifest and marketplace file shapes.

## Choosing a mechanism

| You need | Reach for | Chapter |
|---|---|---|
| A node's brief, loaded by relevance | Skill | 4 |
| Isolation from the parent context | Subagent | 5 |
| A guarantee that does not depend on the model agreeing | Hook | 6 |
| A shareable bundle of all three | Plugin | 7 |
| A human decision before an irreversible action | Hook returning `ask` / `force_ask` | 15 |

Each mechanism solves one class of failure. Skills fix routing. Subagents fix
isolation. Hooks make an edge a guarantee rather than a hope. Plugins fix
distribution. The Agentic Graph Specification in Appendix A formalizes how
these portable pieces compose across any harness.

## Keeping this reference current

The version table at the top of this file is the contract. When you upgrade a
harness, re-check the event catalogue and file locations in that harness's
official documentation, and update the table so readers know what this guide
was verified against. The manuscript's chapter tables are the same source the
book used; this companion file is where the mapping lives for the latest
releases.
