# Graph Engineering with AI Agents: companion code

Working code for *Graph Engineering with AI Agents: Engineering Agentic and
Knowledge Graphs for Complex Workflows* (Alex Merced, Packt).

Every walkthrough in the book runs against the material here. The design goal is
that a reader can clone this repository and reproduce an exercise without
inventing a project, guessing at a fixture, or filling in a helper the book
printed but never defined.

## What this repository is

This repository carries the code, configuration, and reference material for all
fifteen chapters of the book. Each chapter has a directory that collects its
snippets and runnable examples. A `reference/` directory holds the cross-cutting
guide to skills, hooks, and plugins across the five harnesses. The `sample-project/`
directory is the codebase the book builds on from Chapter 1 onward.

## Check it works before you start

```bash
git clone https://github.com/AlexMercedCoder/graph-engineering-with-ai-agents-code
cd graph-engineering-with-ai-agents-code
./verify.sh
```

That runs everything checkable without an agent, a network connection, or an API
key. It should report `passed 18, failed 0`. If it does, every exercise that does
not need a harness will work on your machine.

## What you need

| For | You need |
|---|---|
| The sample project and its tests | Node.js 20 or newer. No `npm install`, ever. |
| The Chapter 9 to 12 tools | Python 3.11 or newer. Standard library only, except where noted. |
| The Chapter 6 hooks | `bash` and `jq`. Each hook exits cleanly with a message if `jq` is missing. |
| Chapter 11 | `pip install pyyaml` |
| Chapter 9 over MCP rather than the CLI | `pip install "mcp[cli]"` |
| Chapter 14, and Chapter 10's optional Neo4j path | Docker |
| Any exercise that drives an agent | One of the five harnesses the book covers |

Nothing here requires a paid API key. The two places the book uses a model
(Chapter 10's extraction, Chapter 12's classifier fallback) ship a deterministic
implementation instead, so the exercise is reproducible and free. Both are marked
in the source with the one-line change that switches them to a real provider.

## Resource index

### Chapter directories

| Chapter | Directory | What is here |
|---|---|---|
| 1 | `ch01-prompt-loop/` | The setup commands, the project rule worth enforcing, and the counterexample that shows why prompts drift |
| 2 | `ch02-sandbox/` | The least-privilege sandbox policy in YAML, JSON, TypeScript, and project-context forms |
| 3 | `ch03-context-wall/` | The seven-task ladder, the three constraints to declare, and `parse-usage.py` to record the curve as CSV |
| 4 | `ch04-routing/` | Four skills, the 20-prompt evaluation set, a scorer that reports the unambiguous/ambiguous split, and the three description versions |
| 5 | `ch05-subagents/` | Worker and dispatcher definitions, the node files, and `run-graph.sh`: the manual execution graph, runnable with any harness that has a non-interactive mode |
| 6 | `ch06-hooks/` | Six hooks and the settings that register them. All verified by `verify.sh` |
| 7 | `ch07-plugin/` | The whole Part 2 graph packaged as an installable plugin |
| 8 | `ch08-budget/` | A split configuration: a small always-loaded core plus three path-scoped rules |
| 9 | `ch09-mcp/` | A working knowledge server with real data, plus `cli.py`, the dependency-free command line surface |
| 10 | `ch10-graph/` | Ten cross-referencing documents, an extraction pipeline into SQLite, three traversal tools, and the 20-question benchmark |
| 11 | `ch11-catalog/` | A semantic layer in the Apache Ossie shape, and lineage validation with the four checks |
| 12 | `ch12-router/` | The retrieval router, its evaluation set, and the evidence document schema |
| 13 | `ch13-desktop-port/` | The port-to-desktop mapping, the terminology, and the design principle (no code to script) |
| 14 | `ch14-observability/` | Jaeger via Docker Compose, the telemetry environment, and the no-tracing audit-log substitute |
| 15 | `ch15-governed-workflow/` | The approval packet and the hook that demands a human decision before irreversible operations |

### Shared and reference material

| Resource | Path | What is here |
|---|---|---|
| The worked project | `sample-project/` | The order-management API the book builds on: four service modules, two repositories, a router, and ten tests |
| Skills, hooks, and plugins across five harnesses | `reference/harness-guide.md` | How Claude Code, OpenAI Codex CLI, Google Antigravity, OpenCode, and Pi implement skills, subagents, hooks, and plugins, with the per-harness file locations and event vocabulary |
| Appendix A | `ags/` | The Chapter 5 migration expressed as an AGS 1.0 document |
| Appendix B | `appendix-b-loro-magagent/` | The MagAgent and Loro command and code snippets that demonstrate AGS in two custom harnesses |
| Verification | `verify.sh` | Runs everything checkable with no agent and no network |

## The harness guide

Chapter 1 through Chapter 9 assume you have at least one of the five harnesses:
Claude Code, OpenAI Codex CLI, Google Antigravity, OpenCode, or Pi. The same
skills, subagents, hooks, and plugins map to a different configuration file and
directory structure in each one. The `reference/harness-guide.md` reference maps
each mechanism onto all five, so you can take the material in this repository and
place it in whichever harness you use.

## Two things the book prints and this repository completes

**Chapter 9, 10, and 11 listings call helpers.** The book shows the tool bodies,
because those carry the argument. `ERROR_CODES`, `search_sections`,
`resolve_entity`, `traverse_incoming`, `compile_to_sql` and the rest are real here.
Each module names the listing it belongs to, so you can read the chapter and the
implementation side by side.

**Chapter 5's migration needs four callback-style modules.** Almost no reader has
those lying around, so `sample-project` provides them, with tests that pass before
the migration and must still pass after it.

## What is not here

- **Chapter 13 has no code to script.** Porting to a desktop surface means
  clicking through a real application. The `ch13-desktop-port/` directory carries
  the mapping of what to port and where each piece already lives.
- **Chapter 15 assembles the pieces from the other directories.** The deployment
  checklist is in the chapter; the components are here.
- **No harness configuration is committed to a fixed tool.** Skills and subagent
  definitions use the open Agent Skills frontmatter. Where a harness needs its own
  format, the chapter shows the translation.

## Reporting a problem

Open an issue. Include the chapter, the command you ran, and the `verify.sh`
output. A failing `verify.sh` line is the fastest thing to fix.

## Licence

Apache 2.0. See `LICENSE`.
