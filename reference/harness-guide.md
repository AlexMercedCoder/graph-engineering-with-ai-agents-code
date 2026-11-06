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
| Claude Code | 2.1.316 | 2026-11-05 | Official hooks and plugin-marketplace references, plus the book's runs |
| OpenAI Codex | CLI 0.166.0 | 2026-11-05 | Official hooks reference, `codex features list`, and the book's runs |
| Google Antigravity | agy CLI 1.4.12 | 2026-11-05 | `agy` help and installed layout; hooks, skills, and rules details from the docs as of agy 1.1.12 (2026-08-13) unless marked |
| OpenCode | 1.19.5 | 2026-11-05 | Official plugins docs, plus the book's runs |
| Pi | 1.4.0 | 2026-11-05 | The docs and changelog shipped with the installed package, plus the book's runs |

Each fact below is either **measured** (seen in a run on the version given) or
**documented** (read in the vendor's documentation for that version). Where the
documentation and the installed release disagreed, the installed release won
and the text says so.

## Quick map

| Harness | Skills root | Subagents root | Hooks live in | Plugins |
|---|---|---|---|---|
| Claude Code | `.claude/skills/` (project), `~/.claude/skills/` (personal) | `.claude/agents/`, `~/.claude/agents/` | `.claude/settings.json`, or a skill/subagent definition | `.claude-plugin/` with `plugin.json` |
| OpenAI Codex | `.codex/` skills directory | `.codex/agents/` | `hooks.json`, or `[hooks]` in `config.toml` | Installed with `codex plugin add` from a marketplace; hooks in the manifest or `hooks/hooks.json` |
| Google Antigravity | `.agents/skills/` (workspace), `~/.gemini/antigravity-cli/skills/` (global) | `.agents/` agents directory | `.agents/hooks.json`, or `~/.gemini/config/hooks.json` | Installed with `agy plugin install` into `~/.gemini/config/plugins/<name>/` (observed, 1.4.12) |
| OpenCode | `.opencode/skills/` (project), `~/.config/opencode/skills/` (user) | `.opencode/agents/` | A plugin module in the project | `.opencode/plugins/`, `~/.config/opencode/plugins/`, or npm packages named in `opencode.json` |
| Pi | `.pi/skills/` or `.agents/skills/` (project), `~/.pi/agent/skills/` or `~/.agents/skills/` (global) | None built in; add them with an extension or a Pi package | A TypeScript extension | Extensions in `~/.pi/agent/extensions/` or `.pi/extensions/`; Pi packages from npm or Git |

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
  in Pi `.pi/skills/` or the standard `.agents/skills/`, which Pi 1.4.0 also
  searches up to the repository root (documented); in Google Antigravity `.agents/skills/`.
- **Organization scope**: applied by enterprise-managed settings where the
  harness supports them.

Google Antigravity follows the same shape: workspace skills in `.agents/skills/` and
global skills under `~/.gemini/antigravity-cli/skills/`. Its frontmatter needs
only `description`; `name` is optional and defaults to the folder name if
absent.

### How much of the skill list reaches the model

Every harness caps the standing cost of the skill list differently, and the cap
decides what happens when a project grows (Chapter 8).

| Harness | What happens to the listing | Status |
|---|---|---|
| Claude Code | Descriptions are shortened or dropped once the list passes its budget, starting with the least-used skills, not alphabetically. A skill listed by name only routes far worse: Chapter 4's routing prompts reached the right skill in 12 of 40 runs with names only, against 29 of 40 with descriptions | Measured, 2.1.316 |
| OpenAI Codex | Skills are listed in up to 2% of the context window (8,000 characters if the window is unknown); `skills.max_context_tokens` raises the limit to 10,000 | Documented, 0.166.0 |
| Google Antigravity | Rules can load by `trigger: glob`; always-on rules share a 20,000-token budget | Documented, November 2026 |
| OpenCode | Loads a subdirectory's `AGENTS.md` along with the first file the agent reads there | Measured, 1.19.5 |
| Pi | Skills are listed in the system prompt; no separate cap is documented | Documented, 1.4.0 |

### If your harness does not support skills

The substitute is a `docs/procedures/` directory and one line in the project
configuration telling the agent which file to read for which job. That
reproduces progressive disclosure by hand at about 60 standing tokens. What you
give up is the routing decision, which moves from the agent to you.

## Subagents

A subagent is a Markdown file with YAML frontmatter, placed in the harness's
agents directory. In Claude Code that is `.claude/agents/` for project scope or
`~/.claude/agents/` for personal scope, with the same three-tier logic as
skills. OpenAI Codex, Google Antigravity, and OpenCode use their own agents
roots with the same shape. Pi ships without subagents by design; its docs
point you to an extension or a Pi package that adds them (documented, 1.4.0).

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
| Claude Code | `.claude/settings.json`, `~/.claude/settings.json`, or a skill/subagent definition | Shell command (or HTTP, MCP tool, prompt, or agent handler), event JSON on stdin; an `if` field such as `"Bash(rm *)"` keeps the hook from starting on calls it doesn't match | The widest catalogue, about thirty events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`, `UserPromptSubmit`, `SubagentStop`, `Stop`, and more | Exit code 2, or JSON `permissionDecision` |
| OpenAI Codex | `hooks.json` or `[hooks]` in `config.toml`, at `~/.codex/` or `<repo>/.codex/` | Shell command or MCP tool with a `matcher`; hooks that an administrator didn't manage must be reviewed and trusted before they run | `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, per-request `PreModelRequest` and `PostModelRequest`, and session events | Exit code 2, or a JSON `decision` |
| Google Antigravity | `.agents/hooks.json` (workspace) or `~/.gemini/config/hooks.json` (global) | Shell command with a `matcher` | `PreToolUse`, `PreInvocation`, `PostInvocation`, plus `PostToolUse` and `Stop` | JSON `decision` with `allow`, `deny`, or `force_ask` |
| OpenCode | A plugin module in `.opencode/plugins/` | TypeScript or JavaScript function | `tool.execute.before`, `tool.execute.after`, plus session, message, and permission events | Throw from the handler |
| Pi | A TypeScript extension in `~/.pi/agent/extensions/` or `.pi/extensions/` | In-process TypeScript via `pi.on()` | Events observe; hooks intercept, including `tool_call` | Return `{ block: true }` |

Two differences change what you write. The bottom two rows are code, not
scripts: a `tool.execute.before` handler that throws on `rm -rf` is the same
guarantee as `guard-bash.sh`, expressed in the language the harness already
runs. And the refusal vocabulary is not uniform: every harness can deny, but
the exact decision values differ, and one harness has historically parsed
`ask` without acting on it. Google Antigravity widens the set with `force_ask`, which
forces a human prompt even in an unattended run. Where a harness cannot prompt,
fall back to `deny` with a rejection message that names the approved path.

A guard has to match the tool that actually edits files. In OpenCode 1.19.5
with an OpenAI GPT model, the agent edits through an `apply_patch` tool rather
than `edit` or `write`, so a guard that checks only those names never fires.
Read the target paths from the patch text, on its `*** Add File:`,
`*** Update File:`, and `*** Delete File:` lines, and from `*** Move to:` lines
for renames (checked November 2026).

Adding context before each prompt maps unevenly across the five:

| Harness | Per-prompt context event | Status |
|---|---|---|
| Claude Code | `UserPromptSubmit` | Measured, 2.1.316 (Chapter 6's `git-context.sh`, about 70 tokens a prompt) |
| OpenAI Codex | `UserPromptSubmit` | Documented, 0.166.0 |
| Google Antigravity | None per prompt; `PreInvocation` runs before every model call | Documented, November 2026 |
| OpenCode | None documented | Documented, 1.19.5 |
| Pi | `before_agent_start` | Documented, 1.4.0 |

Hook cost depends on how the hook runs. A shell hook is a new process per call:
in Chapter 6 a bare script took about 5 ms and each `jq` call added about 25 ms,
while OpenCode's in-process plugin took about 0.018 ms per call (measured,
Claude Code 2.1.316 and OpenCode 1.19.5).

The working hooks are in `ch06-hooks/scripts/`, the Claude Code wiring that
registers them is in `ch06-hooks/settings.json`, and the OpenCode equivalent is
`ch06-hooks/opencode/guards.js`. `ch15-governed-workflow/`
shows the approval gate that demands a human decision in front of irreversible
tool calls.

### Enabling hooks

Hooks are on by default in all five harnesses. OpenAI Codex 0.166.0 lists the
`hooks` feature as stable and enabled (`codex features list`), where 0.147.0
needed `[features] hooks = true`; a user can still turn it off, which is why
administrators pin `[features] hooks = true` in `requirements.toml`. Two OpenAI Codex
checks remain before a hook runs: the feature must not be disabled, and a hook
that isn't administrator-managed must be reviewed and trusted. Hooks that don't
run are ignored silently, so check both before debugging a hook that never
fires.

### Verifying a hook fires

Hooks fail silently more often than they fail loudly. Work through this
sequence, because each step rules out the ones after it.

1. Confirm the harness loaded the hook at all. Claude Code's `/hooks` command
   and OpenAI Codex's `/hooks` command list every active hook and the settings file it
   came from.
2. Confirm hooks are enabled. In OpenAI Codex, `codex features list` shows
   whether `hooks` is on, and an untrusted project hook doesn't run until you
   review it.
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

### The OpenAI Codex plugin shape

OpenAI Codex loads plugin-bundled hooks from `hooks/hooks.json` inside the
plugin root by default, or from the plugin manifest (documented, 0.166.0).
Plugin hook commands receive `PLUGIN_ROOT` and `PLUGIN_DATA` environment
variables, plus `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility
with existing plugin hooks (documented as of 0.147.0, not rechecked). The
`plugin_hooks` feature flag no longer exists in 0.166.0, and plugins install
from marketplaces with `codex plugin add` and `codex plugin marketplace`.

### The Google Antigravity plugin shape

`agy plugin install` puts a plugin in `~/.gemini/config/plugins/<name>/`, with
a `plugin.json` manifest at its root (observed, 1.4.12; the 1.1.12 docs named
`~/.gemini/antigravity-cli/plugins/`). Optional components sit beside the
manifest: `mcp_config.json` for MCP servers, `hooks.json` for event hooks, plus
`skills/`, `agents/`, and `rules/` directories. `agy plugin validate [path]
--strict` checks a manifest and its files, and `agy plugin import` converts a
Claude Code plugin.

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
repository, `git-subdir` for a folder in a monorepo, a `url` for a Git
repository on any host, an `archive` (a zip over HTTPS, with an optional
SHA-256 pin), `npm`, or a `command` that builds the plugin on the installing
machine (documented, 2.1.316). Versioning resolves from the first of: `version`
in `plugin.json`, `version` in the marketplace entry, the Git commit SHA, the
SHA-256 digest, or `unknown`.

Pin a Git-based source with `sha` as well as `ref`. In Chapter 7, moving a tag
to a new commit changed nothing for a source pinned with `sha`, while a source
with only `ref` fetched the changed script into a cache folder still named
`1.0.0` (measured, 2.1.316).

Two permission facts matter before you ship a plugin (measured, 2.1.316, on a
personal claude.ai login with no managed settings):

- A plugin's own `settings.json` can't bring allow rules with it.
- A hook that returns `allow` can't override a project deny rule, but a mod can:
  a call the project denied ran when a plugin's mod approved it. The docs say
  managed settings keep the deny by default; that case wasn't run.

The worked example is `ch07-plugin/team-workflow/`. The manuscript's chapter 7
shows the full manifest and marketplace file shapes.

### Configuration merges

Layered configuration doesn't merge the same way everywhere. OpenCode merges
its config files key by key, and the last matching permission rule wins; a key
keeps the position the earlier file gave it, so a merge can reorder rules
(measured, 1.19.5; the reordering isn't documented). Print the merged
configuration before trusting a rule's order.

## MCP servers

Chapters 9 to 11 register their servers per project so nothing touches your
user configuration. Claude Code 2.1.316 and OpenCode 1.19.5 ran the full
exercises on 2026-11-03; OpenAI Codex 0.166.0 and Pi 1.4.0 ran one connection
check each on 2026-11-05; Google Antigravity wasn't run.

| Harness | Project config | Local (stdio) server | Remote (HTTP) server |
|---|---|---|---|
| Claude Code | `.mcp.json` at the project root | `{"type": "stdio", "command": "python3", "args": [...], "env": {...}}` | `{"type": "http", "url": "...", "headers": {"Authorization": "Bearer ${VAR}"}}` |
| OpenCode | `mcp` key in `opencode.json` | `{"type": "local", "command": ["python3", ...], "environment": {...}}` | `{"type": "remote", "url": "...", "headers": {"Authorization": "Bearer {env:VAR}"}}` |
| OpenAI Codex | `[mcp_servers.<name>]` in `config.toml`, or `-c mcp_servers.<name>.command=...` overrides | `command`, `args`, and `env` keys | `url` with headers |
| Pi | `.pi/mcp.json` (trusted projects only) or `~/.pi/agent/mcp.json`, under `mcpServers` | `command`, `args`, `env` | `url`, `headers`, or OAuth |
| Google Antigravity | User configuration only, through `agy mcp add [-e KEY=value] <name> <command> [args]` | `--type stdio` (default) | `agy mcp add -H "Key: Value" <name> <url>` |

Behavior observed in those runs:

- `claude -p` started a project's `.mcp.json` servers without asking for
  approval. `--mcp-config <file> --strict-mcp-config` uses only the servers in
  that file and excludes user-level servers and claude.ai connectors.
- Claude Code defers MCP tool schemas behind its tool search by default; a tool
  marked with the `anthropic/alwaysLoad` meta key is sent up front. OpenCode
  sends every schema on the first request.
- OpenCode's default permissions ask before reading `*.env` files, and
  `opencode run` treats the unanswered question as a refusal.
- On a 403 for a missing scope, OpenCode tried to step up through the
  authorization server named in the protected resource metadata (discovery,
  then `POST /register`). Claude Code reported a tool error and carried on.
- OpenAI Codex 0.166.0: `codex exec` runs with no approvals, so it refused
  the tool call until `default_tools_approval_mode = "approve"` was set for the
  server, and a project `.codex/config.toml` in an untrusted folder wasn't
  loaded; pass the server with `-c` overrides instead (measured). A server's
  `omit_tools_from` takes `direct`, `deferred`, or `code_mode` (documented).
- Pi has MCP built in from 0.99.0 (changelog); earlier releases need the
  `pi-mcp-adapter` package. Pi 1.4.0 ignores `.pi/mcp.json` until the project
  is trusted, and `PI_CODING_AGENT_DIR` pointed at a scratch folder keeps a
  test away from your own configuration (measured). A server's `exposure` is
  `codemode` (the default), `deferred`, `direct`, or `hidden` (documented).
- Google Antigravity 1.4.12 manages servers with `agy mcp add`, `remove`,
  `list`, `enable`, and `disable`, which write the user's `mcp_config.json` in
  `~/.gemini/config/` (observed; not run against the book's servers).

### Giving a subagent its own server

- Claude Code 2.1.316: an `mcpServers` entry in a subagent's agent file did
  not start the server in four variants; the same entry passed as a list in
  `--agents` JSON did (measured). `--disallowedTools` on the main session also
  removes those tools from its subagents (measured). Parallel subagents with
  byte-identical inline server configs share one server process, so one
  worker exiting can cut off the others (measured; anthropics/claude-code
  issue 84638).
- OpenCode 1.19.5: turn a server's tools on or off per agent with
  `permission` entries such as `"<server>_*": "deny"` or `"allow"`; the older
  `tools` map still works but is deprecated (documented).
- OpenAI Codex: `mcp_servers` in an agent file don't override the parent's
  (documented).

### Connecting a server to Claude Desktop

- Claude's custom connectors use OAuth with the redirect
  `https://claude.ai/api/mcp/auth_callback`. Claude requests the scopes the
  protected resource metadata lists in `scopes_supported`, so a server that
  advertises only a read scope can never be granted more; Client ID Metadata
  Documents are preferred over dynamic client registration (documented;
  checked with `ch13-desktop-port/tools/connector-check.py`, 2026-11-05).
- A desktop extension (`.mcpb`) runs the server locally over stdio with the
  user's own settings, so an identity typed into its configuration is not a
  boundary (measured in Chapter 13).
- Claude Desktop's Chat, Cowork, and Code tabs load plugin skills; Cowork also
  loads hooks and subagents, and has run in the cloud by default since
  2026-10-06 (documented).

### Plugins, write limits, and timeouts for a governed workflow

- Claude Code 2.1.316 names a plugin's MCP tools
  `mcp__plugin_<plugin>_<server>__<tool>`. `--strict-mcp-config` drops a
  plugin's MCP servers but still loads its skills, and
  `ENABLE_CLAUDEAI_MCP_SERVERS=false` keeps claude.ai connectors out (measured
  in Chapter 15).
- Limit writes in Claude Code with `Edit(path)` rules (a `Write(path)` rule
  didn't match) plus `permissions.blockWritesOutsideWorkingDirectories`
  (2.1.314 and later). In OpenCode 1.19.5, use `permission.edit` patterns and
  `external_directory: deny` (both measured).
- Long-running MCP tools: Claude Code's HTTP idle timeout is 5 minutes
  (`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`), and interactive calls move to the
  background after 2 minutes; OpenAI Codex `tool_timeout_sec` defaults to 60
  seconds and Google Antigravity `timeoutSeconds` to 180 (documented). With
  no timeout set, neither Claude Code (76 seconds) nor OpenCode (46 seconds)
  gave up on a slow reviewer (measured).

## Telemetry

| Harness | How tracing is switched on | Notes |
|---|---|---|
| Claude Code 2.1.316 | `CLAUDE_CODE_ENABLE_TELEMETRY=1` and the OTLP environment variables | Project settings can't switch it on (measured). It sends a `traceparent` header to HTTP MCP servers. `input_tokens` excludes cache reads and writes. Hook spans need detailed beta tracing. One `agent_classifier` request per session is missing from the cost events (measured). |
| OpenCode 1.19.5 | `experimental.openTelemetry` plus the endpoint variable | No `traceparent` to MCP servers. About 1,200 internal spans per session, with prompts, responses, and tool content included by default (measured). |
| OpenAI Codex 0.166.0 | `[otel]` with `trace_exporter` in `config.toml` | Documented, not run. |
| Google Antigravity 1.4.12 | No built-in exporter; use hooks | Documented, not run. |
| Pi 1.4.0 | `--mode json` output and `pi.on()` extension events | Documented, not run. |

`--max-budget-usd` in Claude Code stops after the response that crosses the
limit, so it can overshoot by up to one response (measured in Chapter 14).

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
