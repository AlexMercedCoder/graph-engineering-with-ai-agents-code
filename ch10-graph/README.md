# Chapter 10: Surpassing Chunk-Based Limitations

A knowledge graph extracted from ten architecture documents, the traversal tools that
query it over MCP, and a benchmark against a vector retriever over the same documents.

| Path | What it is |
|---|---|
| `docs/` | Ten architecture documents, one per service, about 1,100 words in all, each with sections for overview, data, integrations, configuration, and operations |
| `graph/ontology.py` | Four entity types, five relationship types, their signatures, the extraction prompt, and the alias table |
| `graph/model.yaml` | The same model in the Apache Ossie shape (datasets, relationships, `ai_context`) |
| `graph/extract.py` | The extraction pipeline and incremental refresh |
| `graph/extractions/` | The saved model replies, one per document, with the hash they were made from |
| `graph/traversal.py` | `find_dependents`, `find_dependencies`, `trace_configuration` |
| `graph/server.py` | The three tools over MCP (MCP Python SDK 2.0, `MCPServer`) |
| `graph/query.py` | The same tools from the command line, plus `edge` to show the sentence behind an edge |
| `graph/ladybug_graph.py` | Loads the graph into LadybugDB and runs `find_dependents` as Cypher |
| `eval/chunks.py` | The vector baseline: one chunk per section, `BAAI/bge-small-en-v1.5` through fastembed |
| `eval/chunk_server.py` | `search_docs` over MCP, for the agent benchmark |
| `eval/questions.jsonl` | Twenty questions, ten single-hop and ten multi-hop, with expected entities and the sections that state them |
| `eval/recall.py` | How many of each answer's sections the retriever returns at top-3 and top-5 |
| `eval/run_agents.py` | Asks an agent every question with one MCP server and no built-in tools |
| `eval/grade.py` | Scores recall and, on closed-set questions, precision with a model judge (or `--regex`) |
| `eval/run_graph_side.py` | Calls the traversal tools directly for the ten multi-hop questions |
| `eval/check_refresh.py` | Checks that an incremental refresh matches a full rebuild |
| `eval/check_guards.py` | Feeds the pipeline a reply with one of each extraction error |
| `eval/check_manifest.py`, `deploy/services.txt` | Compares the graph's `Service` nodes with what's deployed; fails on a stale or missing service, warns on one with no edges |
| `eval/time_tools.py` | Times vector search and `find_dependents` at two and four hops, without a model |
| `eval/check_secrets.py` | Checks that extraction refuses a folder holding a credential file or key-like text |
| `runs/` | Real runs from 2026-11-03; see `runs/README.md` |

## Setup

```bash
pip install "mcp>=2.2,<3" fastembed ladybug
```

`extract.py`, `query.py`, `run_graph_side.py`, `check_refresh.py`, and `check_guards.py` need
only the standard library. Re-extraction calls a model through `claude -p`; replace
`call_model()` in `extract.py` to use another client.

## Building and querying the graph

```bash
cd graph
python3 extract.py                 # from the saved extractions, no model call
python3 extract.py --names         # review node names for duplicates
python3 query.py dependents NotificationsAPI 2
python3 query.py dependencies OrderService 2
python3 query.py config PAYMENT_API_KEY
python3 query.py config UserService
python3 query.py edge BillingService NotificationsAPI
python3 ladybug_graph.py           # same five services as dependents NotificationsAPI 2
```

Expected first line of a fresh build: `10 added, 0 unchanged (0 model calls, $0.0000); graph has 27 nodes, 30 edges`.

`python3 extract.py --model` re-extracts any document whose hash (document plus prompt) changed
and patches the graph by document. `--rebuild` starts from an empty graph. Changing the prompt
in `ontology.py` re-extracts every document.

## Registering the server

```json
{
  "mcpServers": {
    "project-graph": { "command": "python3", "args": ["ch10-graph/graph/server.py"] }
  }
}
```

## The benchmark

```bash
python3 eval/recall.py
python3 eval/run_agents.py --harness claude --side chunks --runs 2 --out results/
python3 eval/run_agents.py --harness claude --side graph --runs 2 --out results/
python3 eval/run_agents.py --harness opencode --side chunks --runs 2 --out results/
python3 eval/run_agents.py --harness opencode --side graph --runs 2 --out results/
python3 eval/grade.py results/
```

Run `run_agents.py` with a Python that has `mcp` and `fastembed`, because it starts the servers
with the same interpreter. Results from 2026-11-03 (Claude Code 2.1.316 with `claude-opus-5-5`,
OpenCode 1.19.5 with `openai/gpt-6.1-sol`, judge `claude-sonnet-5-5`). Fully correct out of 20 per
cell; recall, precision, calls, input tokens, and Claude Code's reported cost per multi-hop question:

| Harness | Retrieval | Single-hop | Multi-hop | Recall | Precision | Calls | Input tokens | Cost |
|---|---|---|---|---|---|---|---|---|
| Claude Code | Vector search | 20/20 | 20/20 | 1.00 | 1.00 | 4.5 | 19,787 | $0.076 |
| Claude Code | Graph traversal | 14/20 | 18/20 | 1.00 | 0.98 | 2.4 | 13,462 | $0.046 |
| OpenCode | Vector search | 20/20 | 18/20 | 0.99 | 0.99 | 4.2 | 6,900 | n/a |
| OpenCode | Graph traversal | 14/20 | 18/20 | 1.00 | 0.98 | 1.2 | 2,926 | n/a |

One-shot retrieval (`recall.py`) returned every supporting section for 10/10 single-hop and 1/10
multi-hop questions at top-3 (mean 43% of sections), and 3/10 multi-hop at top-5 (mean 59%).

## Checks

```bash
cd eval
python3 run_graph_side.py     # graph tools answered 10/10 multi-hop questions exactly
python3 check_refresh.py      # patched graph matches a full rebuild
python3 check_guards.py       # all guards fired
```
