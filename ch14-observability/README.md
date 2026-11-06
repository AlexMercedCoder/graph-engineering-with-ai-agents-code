# Chapter 14: Solving the Agent "Black Box" Failure

Traces from Claude Code and OpenCode, collected on your laptop; the Chapter 10 graph
server with spans of its own; a regression test that reads a trace and names the
graph a failure came from; and policy checks for spend, access, and regression.
No Docker, no account, no trace backend to sign up for.

## Setup

```bash
pip install -r requirements.txt        # MCP Python SDK 2.2 or later (tested 2.0.0 and 2.3.0) and the OpenTelemetry SDK
python3 tools/make-test-tokens.py      # writes config/test-tokens.json and .env (gitignored)
python3 collector.py --out telemetry   # listens on http://127.0.0.1:8814
```

The graph server reads the Chapter 10 graph in `../ch10-graph/graph/project-graph.db`;
`eval/run.sh` builds it with `extract.py` if it's missing.

## What's here

| Path | What it is |
|---|---|
| `collector.py` | An OTLP/HTTP receiver (protobuf or JSON, chunked or not) that writes `spans.jsonl`, `logs.jsonl`, and `metrics.jsonl`, hashes identity attributes (HMAC when `COLLECTOR_HASH_KEY` is set), drops content attributes by exact name unless started with `--keep-content`, and with `--agent-spans-only` reduces other spans to their IDs, name, and times |
| `env.sh` | The Claude Code variables for exporting metrics, events, and traces to the collector, including `OTEL_LOG_TOOL_DETAILS=1`, which the triage needs |
| `graphspans.py` | Rebuilds the execution graph from exported spans: Claude Code, OpenCode, and MCP SDK names mapped onto five node kinds; `tree` prints it |
| `server/graph_server.py` | The Chapter 10 tools over Streamable HTTP on port 8815, with a span per tool call, scopes, a partial-coverage line in the reply, and `GRAPH_AUDIT_LOG` for harnesses without tracing |
| `hooks/audit-trace.sh` | The Chapter 6 audit hook (with its secret redaction) plus `agent_id` and the skill name |
| `read-audit.sh` | The route question answered from that audit log |
| `eval/skills/` | The `blast-radius` skill and the three faulty versions the regression test uses |
| `eval/expected.json` | The expected route and evidence for the blast-radius question |
| `eval/triage.py` | The three triage questions and the verdict for one run folder |
| `eval/run.sh` | One traced session: collector, server, harness, triage. `COLLECT=production` runs the collector without content and with `--agent-spans-only`; `PORT_OFFSET` moves the ports |
| `eval/run-notrace.sh` | The same question with no telemetry: the audit hook and the server's `GRAPH_AUDIT_LOG` |
| `eval/check-project-settings.sh` | Checks that a project's `.claude/settings.json` can't switch telemetry on (one short model call) |
| `eval/run-matrix.sh`, `eval/summarize.py` | Every condition in both harnesses, and the table |
| `eval/check-saved-runs.py` | Reruns the triage over the published runs and compares each verdict (used by `verify.sh`) |
| `policy.json`, `policy.py` | The spend, access, and regression policies, and the checks (`spend`, `access`, `baseline`, `regress`) |
| `baseline.json` | The regression baseline recorded from the published baseline runs |
| `tools/` | Test tokens, the instrumentation, collector, and redaction checks, the overhead benchmark, and the run sanitizer |
| `docker-compose.yml` | Optional: Jaeger 2.22.0 as a trace viewer, for development (not used in the chapter's runs) |
| `runs/` | Published runs from 2026-11-05; see `runs/README.md` |

## Exporting traces

From Claude Code, source `env.sh` in the shell you start it from (Claude Code ignores these
variables in a repository's `.claude/settings.json`). From OpenCode, set
`OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:8814` and add
`"experimental": {"openTelemetry": true}` to `opencode.json`. Then:

```bash
python3 graphspans.py tree telemetry
```

## The regression test

```bash
bash eval/run.sh claude baseline runs/my-run          # one session; prints the triage
OPENCODE_MODEL=openai/gpt-6.1-sol bash eval/run.sh opencode depth-cap runs/my-run-2
bash eval/run-matrix.sh runs/my-matrix 3              # every condition, both harnesses
```

Conditions: `baseline`, `bad-description` (the skill's description rewritten for release
notes), `depth-cap-silent` (server depth cap 1, no partial-coverage line), `depth-cap` (cap 1,
with the line), `soft-body` (the skill asks for direct dependents only), and `stale-rule` (the
skill tells the agent to leave two services out). `ROLE=contractor` runs with the token that
lacks `config:read`; `QUESTION=...` replaces the question.

## Policies

```bash
python3 policy.py spend runs/2026-11-05-triage/claude-baseline-*
python3 policy.py access runs/2026-11-05-access/*
python3 policy.py baseline runs/2026-11-05-triage/*-baseline-* > baseline.json
python3 policy.py regress baseline.json runs/2026-11-05-triage/*-depth-cap-silent-*
```

Each command exits 1 when a run breaks the policy.

## Checks without a model

```bash
python3 tools/check-instrumentation.py      # spans and the coverage line at depth caps 4 and 1
python3 eval/check-saved-runs.py            # the triage still gives every published verdict
bash tools/check-redaction.sh               # fake secrets don't reach the audit log
python3 collector.py --out /tmp/c & python3 tools/check-collector.py /tmp/c   # identity hashed, content dropped
```
