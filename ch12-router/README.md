# Chapter 12: Harmonizing Knowledge and Action

A retrieval router in front of the four knowledge paths from Part 3, one MCP server that
serves all four with evidence envelopes, the evidence document and its checker, and a
retrieval worker that keeps retrieval out of the main session.

| Path | What it is |
|---|---|
| `router.py` | `RULES`, `route()` (clause by clause, first match wins), the optional model fallback (`ROUTER_MODEL`), and the redacted fallthrough log (`ROUTER_LOG`) |
| `knowledge_server.py` | MCP server `project-knowledge`: `route_question`, `check_evidence`, and the nine retrieval tools of Chapters 9 to 11, each returning `{"evidence": ..., "result": ...}` |
| `evidence.py` | `envelope()`, `check()`, and `python3 evidence.py check <file>` |
| `evidence_schema.json` | The evidence document, schema version 1 |
| `agents/retrieval-worker.md` | The retrieval worker (Claude Code subagent format) |
| `agents/build_agents_json.py` | Prints the worker as `--agents` JSON with the knowledge server attached to it |
| `skills/act-on-evidence/` | The rules for acting on evidence documents |
| `skills/retrieve-evidence/` | The worker's instructions as a skill, for retrieval inside the main session |
| `eval/routing.jsonl` | 42 labeled questions: 26 from Chapters 10 and 11, 6 error-code and schema questions, and 10 worded to avoid the rules |
| `eval/route_eval.py` | Routing accuracy, mis-routes by what they cost, and the model's time and cost |
| `eval/combined.jsonl` | Four questions that ask for a set of services and one or two facts |
| `eval/run_routed.py` | Chapter 10's questions (or `--questions`) in four setups: `vector`, `graph`, `routed`, `free` |
| `eval/both_server.py` | Chapter 10's vector and graph tools in one server, for `free` and fan-out routes |
| `eval/grade_combined.py` | Grades the combined questions with Chapter 10's model judge |
| `eval/brief_task.md` | The six-question brief task (all four paths, two refusals) |
| `eval/run_subcycle.py` | Runs the brief task with retrieval `inline` or in the `worker` |
| `eval/grade_brief.py` | Scores the briefs, validates their evidence, and reports the main session's context |
| `eval/act_fix.md`, `eval/act_refuse.md` | Two tasks that change, or decline to change, Chapter 9's staging `payments.conf` (`run_subcycle.py --act`) |
| `eval/grade_act.py` | Scores the act tasks from the edited file |
| `eval/vector_probes.py` | The probes behind `search_docs`' confidence thresholds |
| `eval/check_router.py` | Deterministic checks, standard library only |
| `eval/check_server.py` | Envelope checks against the real Chapter 9 to 11 data |
| `runs/` | Real runs from 2026-11-05; see `runs/README.md` |

## Setup

From the repository root:

```bash
pip install "mcp>=2.2,<3" fastembed pyyaml
python3 ch10-graph/graph/extract.py
python3 ch11-catalog/warehouse/seed.py
```

`router.py`, `evidence.py`, `eval/route_eval.py`, and `eval/check_router.py` need only the
standard library. The model fallback and the agent runners call `claude -p` or `opencode run`.

## Routing

```bash
cd ch12-router
python3 router.py "Which services call the PaymentsAPI directly, and why does PaymentsService never retry a declined payment?"
python3 eval/route_eval.py                # rules only: routing accuracy: 36/42
python3 eval/route_eval.py --model        # rules, then claude-haiku-5-5 for the 9 unmatched
python3 eval/route_eval.py --model-only
ROUTER_LOG=logs/fallthrough.jsonl python3 router.py "Who gets hurt if we take the users service offline?"
```

`logs/` is in `.gitignore`. The log redacts email addresses and token-shaped strings; it
doesn't catch every secret, so keep it local.

## Registering the server

Claude Code, without touching your user configuration:

```bash
cat > mcp.json <<'JSON'
{"mcpServers": {"project-knowledge": {"command": "python3", "args": ["<path>/ch12-router/knowledge_server.py"],
  "env": {"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}}}}
JSON
claude --mcp-config mcp.json --strict-mcp-config
```

To give the server to the retrieval worker only, attach it to the worker and leave it out of the
session configuration:

```bash
claude --agents "$(python3 ch12-router/agents/build_agents_json.py)" \
       --strict-mcp-config --mcp-config '{"mcpServers":{}}'
```

In Claude Code 2.1.316 an inline `mcpServers` entry in the agent *file* didn't start the server in
our tests (list and mapping forms, with and without `--strict-mcp-config`), so pass the worker with
`--agents`. Parallel workers with identical inline server configurations share one server process
(anthropics/claude-code issue 84638), so send one worker call per task.

OpenCode, in `opencode.json` (the `tools` map is what we ran on 1.19.5; the OpenCode docs now prefer
`permission` with `"project-knowledge_*": "deny"` and an `"allow"` in the agent):

```json
{"mcp": {"project-knowledge": {"type": "local", "command": ["python3", "<path>/ch12-router/knowledge_server.py"],
  "environment": {"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}}},
 "tools": {"project-knowledge_*": false},
 "agent": {"retrieval-worker": {"mode": "subagent", "description": "...", "prompt": "...",
   "tools": {"project-knowledge_*": true, "write": false}}}}
```

The worker queries governed data as whatever identity its configuration sets, so whoever can
edit that configuration chooses the identity.

## Results (2026-11-05)

Claude Code 2.1.316 (`claude-opus-5-5`; `claude-haiku-5-5` for the model classifier and the
worker), OpenCode 1.19.5 (`openai/gpt-6.1-sol`).

Routing, 42 labeled questions, four passes for each model setup:

| Classifier | Correct | Model calls | Time per pass | Cost per pass |
|---|---|---|---|---|
| Rules only | 36 | 0 | under 3 ms | $0 |
| Rules, then the model | 40 to 42 | 9 | about 45 s | $0.003 to $0.004 |
| Model only | 39 to 42 | 42 | about 190 s | $0.010 to $0.024 |

Chapter 10's twenty questions, two runs per question; vector-only and graph-only are Chapter
10's runs (`../ch10-graph/runs/2026-11-03-benchmark/final/`):

| Harness | Setup | Single-hop | Multi-hop | Calls | Input tokens | Cost |
|---|---|---|---|---|---|---|
| Claude Code | Vector only | 20/20 | 20/20 | 3.0 | 15,195 | $0.058 |
| Claude Code | Graph only | 14/20 | 18/20 | 2.8 | 13,675 | $0.045 |
| Claude Code | All four tools, no router | 20/20 | 20/20 | 3.2 | 14,026 | $0.047 |
| Claude Code | Routed | 20/20 | 20/20 | 2.0 | 11,566 | $0.041 |
| OpenCode | Vector only | 20/20 | 18/20 | 2.6 | 4,701 | n/a |
| OpenCode | Graph only | 14/20 | 18/20 | 1.7 | 3,354 | n/a |
| OpenCode | All four tools, no router | 20/20 | 19/20 | 1.8 | 3,657 | n/a |
| OpenCode | Routed | 20/20 | 18/20 | 1.2 | 2,664 | n/a |

Combined questions, two runs each:

| Harness | Setup | Fully correct | Calls | Input tokens | Cost |
|---|---|---|---|---|---|
| Claude Code | Graph only | 0/8 | 7.6 | 21,109 | $0.061 |
| Claude Code | Vector only | 8/8 | 3.4 | 14,800 | $0.059 |
| Claude Code | Routed to both | 8/8 | 3.6 | 14,413 | $0.050 |
| OpenCode | Graph only | 0/8 | 8.2 | 7,984 | n/a |
| OpenCode | Vector only | 8/8 | 2.4 | 4,894 | n/a |
| OpenCode | Routed to both | 8/8 | 3.5 | 4,690 | n/a |

The brief task, three runs per setup:

| Harness | Retrieval | Correct | Main requests | Main input tokens | Largest request | Worker input tokens | Time | Cost |
|---|---|---|---|---|---|---|---|---|
| Claude Code | Inline | 18/18 | 8.0 | 122,512 | 22,303 | none | 74 s | $0.342 |
| Claude Code | Worker | 18/18 | 3.0 | 40,944 | 17,443 | 58,191 | 101 s | $0.223 |
| OpenCode | Inline | 18/18 | 9.0 | 110,723 | 16,397 | none | 107 s | n/a |
| OpenCode | Worker | 18/18 | 4.3 | 52,023 | 14,885 | 26,417 | 187 s | n/a |

The act tasks, twice per harness with the worker: `act_fix` set `AUTH_HOLD_MINUTES=60` (the
schema default, above `CAPTURE_DELAY_MINUTES=15`) and changed nothing else in 4 of 4 runs;
`act_refuse` left the file unchanged in 4 of 4.

## Checks

```bash
cd ch12-router/eval
python3 check_router.py     # all router checks passed
python3 check_server.py     # all server checks passed
```
