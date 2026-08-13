# Graph Engineering with AI Agents: companion code

Working code for *Graph Engineering with AI Agents: Engineering Agentic and
Knowledge Graphs for Complex Workflows* (Alex Merced, Packt).

Every walkthrough in the book runs against the material here. The design goal is
that a reader can clone this repository and reproduce an exercise without
inventing a project, guessing at a fixture, or filling in a helper the book
printed but never defined.

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

## The worked project

`sample-project/` is the codebase the book builds on from Chapter 1 onward. It is
a small order-management API: four service modules, two repository classes, a
router, and ten tests.

```bash
cd sample-project
npm test        # 10 tests, no dependencies
npm run lint    # dependency-free formatter, so the Chapter 6 hooks have something real to run
```

It is shaped for the exercises rather than for realism. Specifically:

- The four modules in `src/services/` use a **callback-style** database API. Moving
  them to the repository classes in `src/repositories/` is Chapter 5's migration,
  and it is the reason those services look dated.
- `payments` has **no repository yet**. Chapter 5's fourth module is the one with no
  worked answer, on purpose.
- `src/db.js` is an in-memory fake, so the tests run with no database and no setup.
- There are **no dependencies at all**. Tests use the built-in Node test runner and
  the formatter is 30 lines in `scripts/lint.js`. A reader on a locked-down
  machine, a plane, or a corporate proxy can still do every exercise.

## Chapter map

| Chapter | Directory | What is here |
|---|---|---|
| 1, 2 | `sample-project/` | The project, the ten-file repository the chapters ask for |
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
| 14 | `ch14-observability/` | Jaeger via Docker Compose, the telemetry environment, and the no-tracing audit-log substitute |
| Appendix A | `ags/` | The Chapter 5 migration expressed as an AGS 1.0 document |

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

- **Chapter 13** ports the system to a desktop surface. That is a manual exercise
  against Claude Desktop or an equivalent, and there is nothing to script.
- **Chapter 15** assembles the pieces from the other directories. The deployment
  checklist is in the chapter; the components are here.
- **No harness configuration is committed to a fixed tool.** Skills and subagent
  definitions use the open Agent Skills frontmatter. Where a harness needs its own
  format, the chapter shows the translation.

## Reporting a problem

Open an issue. Include the chapter, the command you ran, and the `verify.sh`
output. A failing `verify.sh` line is the fastest thing to fix.

## Licence

Apache 2.0. See `LICENSE`.
