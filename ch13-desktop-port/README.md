# Chapter 13: Bridging the Developer-Analyst Divide

Chapter 13 ports the terminal system to a UI-native desktop surface. This is the
one exercise in the book with nothing to script: porting to a desktop surface
means clicking through a real application, so this directory carries no runnable
code. What it does carry is the mapping of what gets ported and where each piece
already lives in this repository.

## What you port

| System component | Where it already lives | What changes on a desktop surface |
|---|---|---|
| Skills | `ch04-routing/skills/` | Already in the six portable Agent Skills frontmatter fields, so they upload to a validating surface unchanged |
| Knowledge server | `ch09-mcp/` | Becomes the payload behind a connector, exposed to the surface through MCP |
| Router | `ch12-router/` | Either wrapped as a server the surface calls, or replaced by the surface's native model routing |
| Hooks and permission gates | `ch06-hooks/`, `ch15-governed-workflow/` | Cannot run locally on most UI-native surfaces; must move to the server side |

## The design principle

The chapter's central design principle transfers even if you never ship to a
desktop: **anything you cannot enforce on the client must be enforced on the
server.** A UI-native surface has restricted or absent shell access and a
filesystem scope granted explicitly rather than inherited from a working
directory, so every guarantee that depended on a local hook or a local file
system moves into the server.

## Terminology used in the chapter

- **Surface**: a place a user meets the agent, such as a terminal, a desktop
  application, an IDE panel, or a chat window.
- **Connector**: a configured link from a surface to a remote MCP server. The
  user authenticates once, and the surface can then call that server's tools.
- **Extension bundle**: a packaged MCP server, with its dependencies, installed
  onto the user's machine. Claude Desktop calls the format `.mcpb`.
- **UI-native**: a surface built as a graphical application first, where the
  terminal is not part of the experience.

A desktop build of the same harness (Claude Code Desktop, for example) shares
the engine, configuration, MCP servers, hooks, skills, plugins, and permission
rules with its CLI, so nothing in this chapter applies to that case. The chapter
targets the distinct UI-native chat surface instead.
