# Chapter 7 runs, 2026-11-03

Claude Code 2.1.316 (`claude-opus-5-5` as the main model) and OpenCode 1.19.5
(`openai/gpt-6.1-sol`). Every session ran headless on a fresh committed copy of `sample-project/`,
with `--setting-sources project,local` for Claude Code, and loaded plugins with `--plugin-dir`
pointing outside the project. Install, marketplace, and version commands ran in a throwaway
`CLAUDE_CONFIG_DIR`; the author's own Claude Code settings and plugin records were checked by
checksum before and after and didn't change. Claude Code `init` events are removed and local paths
replaced with placeholders; subagent transcripts keep user and assistant messages only.

| Folder | What it tests |
|---|---|
| `2026-11-03-install/` | Installing from a local marketplace, `claude plugin details`, version pinning and updates from a Git source, and a plugin with `skills/` inside `.claude-plugin/` |
| `2026-11-03-namespacing/` | Plugin skill and agent names, a leftover project skill and agent beside the plugin's, two plugins with the same skill name, a preloaded skill inside a plugin agent, and a plugin agent's `hooks` field |
| `2026-11-03-collisions/` | `release-tools` writing into a folder `team-workflow` protects, its 1.1.0 fix, and a plugin whose hook paths still point into the project |
| `2026-11-03-claude-md/` | Conflicting instructions in a parent-folder CLAUDE.md, the project CLAUDE.md, CLAUDE.local.md, and a path-scoped rule |
| `2026-11-03-precedence/` | Model choice across project and local settings, permission merging in Claude Code, and the same deny across OpenCode configuration layers |
