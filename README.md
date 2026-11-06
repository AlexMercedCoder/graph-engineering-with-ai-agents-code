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
key. It should report `passed 65, failed 0` with every optional package installed. Sections that need PyYAML, the MCP SDK (`pip install "mcp>=2.2,<3"`), OpenTelemetry, numpy, the AGS validator, or the `claude` command print a `skip` line instead of failing when the package is missing. If it does, every exercise that does
not need a harness will work on your machine.

## What you need

| For | You need |
|---|---|
| The sample project and its tests | Node.js 20 or newer. No `npm install`, ever. |
| The Chapter 9 to 15 tools | Python 3.11 or newer. Standard library only, except where noted. |
| The Chapter 6 hooks | `bash` and `jq`. Each hook exits cleanly with a message if `jq` is missing. |
| Chapter 11 | `pip install pyyaml` |
| The MCP servers in Chapters 9 to 15 | `pip install "mcp>=2.2,<3"` (earlier 2.x releases have published security advisories) |
| Chapter 14, and Chapter 10's optional Neo4j path | Docker |
| Any exercise that drives an agent | One of the five harnesses the book covers |

`verify.sh` needs no API key. The two places the tools call a model (Chapter 10's
extraction and Chapter 12's classifier fallback) are off by default: Chapter 10
rebuilds the graph from the saved extractions in `ch10-graph/graph/extractions/`,
and Chapter 12 routes by rules alone. Pass `--model` to either to call a model
through `claude -p`.

## Resource index

### Chapter directories

| Chapter | Directory | What is here |
|---|---|---|
| 1 | `ch01-prompt-loop/` | The setup commands, the three exercises, and transcripts from four real runs of the instruction-decay exercise |
| 2 | `ch02-sandbox/` | Per-harness permission and sandbox configuration, the verification exercise, and real runs of it in Claude Code, OpenAI Codex, Google Antigravity, and OpenCode, including configurations that pass |
| 3 | `ch03-context-wall/` | The seven-task ladder and its rules, scripts to measure payloads, score tasks, and record the curve, and real ladder, compaction, and stress-test runs in Claude Code and OpenAI Codex |
| 4 | `ch04-routing/` | Four skills, the 20-prompt routing evaluation with a runner for Claude Code and OpenCode, a scorer, four description versions, and 320 real routing sessions plus access, tool-rule, and fork tests |
| 5 | `ch05-subagents/` | The `test-runner`, `module-migrator`, and `migration-dispatcher` subagents, the node files and `run-graph.sh` (the execution graph as a shell script), and real runs of isolation, dispatching, an agent team, subagent memory, and the script |
| 6 | `ch06-hooks/` | Seven hook scripts (path guards that match whole segments, secret masking in the audit log, a context hook, and a stop hook that flags changed assertions), the settings that register them, an OpenCode plugin with the same guards, `tests/` fixtures run by `verify.sh`, and real blocking, feedback, audit, latency, prompt-handler, and trust runs |
| 7 | `ch07-plugin/` | The Part 2 graph packaged as the `team-workflow` plugin (rebuilt from Chapters 4 to 6 by `tools/sync-from-chapters.sh`), `release-tools` 1.0.0 and 1.1.0, a `book-platform` marketplace, `ci/` install and version-bump checks, `experiments/` mod and hook deny tests, and real install, pinning, namespacing, collision, precedence, and layering runs |
| 8 | `ch08-budget/` | The split configuration, the 146-line guide and its pruned version, `loaded-context.py`, `check-budget.py` for a CI ceiling on the fixed part, compressed, grouped, and names-only skill sets with a routing runner, and real pricing, loading, compaction, listing, deferral, budget-check, names-only, and cross-harness runs |
| 9 | `ch09-mcp/` | The knowledge server on MCP Python SDK 2.x over stdio and Streamable HTTP with bearer-token scopes, its teaching skill, the gate, interface, and timing checks, `cli.py`, and runs in Claude Code, OpenCode, OpenAI Codex, and Pi |
| 10 | `ch10-graph/` | Ten cross-referencing documents, a model-backed extraction pipeline with saved extractions, incremental refresh, and a credentials guard, a SQLite graph (and LadybugDB for Cypher), the graph MCP server, a vector-search baseline, the 20-question benchmark with its grader, and a deployment-manifest check |
| 11 | `ch11-catalog/` | A semantic layer in the Apache Ossie shape over a local SQLite warehouse, lineage validation with a recorded catalog revision, a SQL-checking hook, and a governed catalog MCP server with its skill and benchmark |
| 12 | `ch12-router/` | The retrieval router (rules plus an optional model fallback, with a redacted fallthrough log), one MCP server over the Chapter 9 to 11 paths with evidence envelopes and `check_evidence`, a retrieval worker passed with `--agents`, the `act-on-evidence` skill, and routing, combined-question, worker, and act runs |
| 13 | `ch13-desktop-port/` | Chapter 11's governed-data tools as an OAuth remote connector (identity from the token), a plugin and marketplace for Claude Desktop's Chat and Cowork, a desktop-extension (`.mcpb`) build for contrast, a sign-in checker against Claude's connector requirements, and agent runs through the connector |
| 14 | `ch14-observability/` | A local OTLP collector with identity hashing and content dropping, the Chapter 10 graph server with spans and scopes, span-tree reconstruction for Claude Code and OpenCode, the triage fault matrix, spend, access, and regression policy checks, and the no-tracing audit substitute |
| 15 | `ch15-governed-workflow/` | The assembled workflow: Chapter 12's knowledge server over HTTP, the `change-config` skill, a `change-gate` MCP server with a signed approval store and approval packets built from re-run sources and graph traversal, the `governed-change` plugin and marketplace, the workflow as an AGS document, a preflight check, LedgerService onboarding, and runs (scenario matrix, scaled graph, client timeouts, final code) |
| Appendix A | `ags/` | Chapter 5's execution graph as a validated AGS 1.0 document (`migrate-order-service.agraph.yaml`) |
| Appendix B | `appendix-b-loro-magagent/` | MagAgent, Loro, and MagGraph setup, scripted mock sessions, and runs of graph criteria, policy refusals, role-checked gates, and a read-only MagGraph MCP server |

### Shared and reference material

| Resource | Path | What is here |
|---|---|---|
| The worked project | `sample-project/` | The order-management API the book builds on: four service modules, two repositories, a router, and ten tests |
| Skills, hooks, and plugins across five harnesses | `reference/harness-guide.md` | How Claude Code, OpenAI Codex, Google Antigravity, OpenCode, and Pi implement skills, subagents, hooks, and plugins, with the per-harness file locations and event vocabulary |
| Appendix A | `ags/` | The Chapter 5 migration expressed as an AGS 1.0 document |
| Appendix B | `appendix-b-loro-magagent/` | The MagAgent and Loro command and code snippets that demonstrate AGS in two custom harnesses |
| Verification | `verify.sh` | Runs everything checkable with no agent and no network |

## The harness guide

Chapter 1 through Chapter 9 assume you have at least one of the five harnesses:
Claude Code, OpenAI Codex, Google Antigravity, OpenCode, or Pi. The same
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
