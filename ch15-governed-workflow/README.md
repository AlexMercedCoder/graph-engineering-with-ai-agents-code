# Chapter 15: Shipping the Governed Agentic Workflow

One workflow assembled from the earlier chapters: it fixes a failing service by
changing its deployed configuration, from evidence, and holds production
changes for a reviewer. The knowledge side is Chapter 12's server over the
Chapter 9 to 11 data; the execution side is a skill, Chapter 12's evidence
skills, and Chapter 6's audit hook, packaged as a plugin (Chapter 7); traces go
to Chapter 14's collector. The new parts are the `change-config` skill and the
`change-gate` server.

## Setup

From the repository root:

```bash
pip install -r ch15-governed-workflow/requirements.txt   # MCP SDK 2.2+, fastembed, PyYAML, OpenTelemetry, AGS validator
python3 ch10-graph/graph/extract.py
python3 ch11-catalog/warehouse/seed.py
cd ch15-governed-workflow
python3 tools/make-test-tokens.py        # config/: agent tokens and reviewer keys, mode 600, eight hours
python3 tools/seed-deploy.py --fault production
```

`config/` and `state/` are in `.gitignore`. You also need `jq` (the audit hook)
and Claude Code or OpenCode.

## What's here

| Path | What it is |
|---|---|
| `servers/knowledge_http.py` | Chapter 12's `project-knowledge` tools over Streamable HTTP on 8817, behind a token with `knowledge:read` |
| `servers/gate_server.py` | `change-gate` on 8818: `read_config` and `propose_change`. Values are checked against their schema type; staging applies at once except endpoint keys and low-confidence evidence; everything else builds a packet, files a request, and waits up to `GATE_TIMEOUT` seconds (default 120) for a signed decision |
| `servers/common.py` | Paths, the test-token verifier, tracing to `COLLECTOR`, and Chapter 14's `traceparent` adapter |
| `gate/approvals.py` | The approval store: requests with an action digest and expiry, signed decisions, the decision log (`state/decisions.jsonl`) |
| `gate/approve.py` | The reviewer's command line: `list`, `show`, `approve`, `reject --reason` |
| `gate/reviewer.py` | A scripted reviewer for the evaluation runs (`approve`, `reject "<reason>"`, or `ignore`) |
| `marketplace/` | The `platform-workflows` marketplace and the `governed-change` plugin: three skills, the audit hook, and the two server addresses |
| `graph/change-config.agraph.yaml` | The workflow as an AGS 1.0 document (validates with `ags-validate --strict`) |
| `tools/make-test-tokens.py`, `tools/seed-deploy.py` | Test credentials; deployed configurations from Chapter 9, with an optional fault |
| `eval/check_gate.py` | The gate's guarantees, without a model |
| `eval/check-install.sh` | Installs the plugin into a throwaway configuration and compares the components |
| `eval/check_trace.py` | Checks that a Claude Code run left a complete trace |
| `eval/preflight.sh` | The deployment checklist: packaging, copies against their sources, the knowledge side, the gate, server tokens, and traces |
| `eval/scenarios.json`, `eval/run.py`, `eval/run-matrix.sh`, `eval/grade.py` | The scenarios, one session, every session, and the grades |
| `tools/sanitize-runs.py` | Prepares run folders for publishing |
| `scale/` | Onboarding a new service (LedgerService) into a copy of the graph: `onboard.sh`, its document, and its saved extraction |
| `runs/` | Published runs, sanitized; see `runs/README.md` |

## Running it

Start the servers (two terminals), then the harness:

```bash
cd servers && python3 knowledge_http.py
cd servers && python3 gate_server.py
```

Start the session from an empty folder, never from this one: `state/` and
`config/` hold the deployed files, the approval store, and the reviewer keys.
The permission settings limit the agent's writes to `report.md`:

```bash
CH15=$(pwd)
set -a; . "$CH15/config/test-tokens.env"; set +a
cd "$(mktemp -d)"
ENABLE_CLAUDEAI_MCP_SERVERS=false claude -p "Production payment captures are failing with error E4021. Fix the production payments configuration." \
  --plugin-dir "$CH15/marketplace/plugins/governed-change" \
  --setting-sources project,local --max-turns 40 --tools "Skill,Write" \
  --allowedTools mcp__plugin_governed-change_project-knowledge mcp__plugin_governed-change_change-gate Skill "Edit(/report.md)" \
  --settings '{"permissions": {"blockWritesOutsideWorkingDirectories": true}}'
```

While it waits, decide as a reviewer from a third terminal:

```bash
python3 gate/approve.py list
python3 gate/approve.py show <request-id>
python3 gate/approve.py approve <request-id> --as dana
```

Plugin MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`. In Claude
Code 2.1.316, `--strict-mcp-config` drops the plugin's servers along with your
own (its skills still load), so leave it off and set
`ENABLE_CLAUDEAI_MCP_SERVERS=false` to keep claude.ai connectors out.

The evaluation runs one session per scenario and harness, with the scripted
reviewer:

```bash
python3 eval/run.py --harness claude --scenario fix-approve --run 1 --out runs/mine
bash eval/run-matrix.sh runs/mine 2
python3 eval/grade.py runs/mine/*/
```

## Checks without a model

```bash
python3 eval/check_gate.py          # all gate checks passed
bash eval/check-install.sh          # Skills 3, Hooks 3, MCP servers 2
bash eval/preflight.sh              # uses ports 8817 and 8818
bash scale/onboard.sh               # the manifest check fails, then passes
```

## Before you deploy it

- Replace the `127.0.0.1` addresses in the plugin's `.mcp.json` with your
  servers, and put both behind the OAuth connector from Chapter 13.
- Keep the approval store and the reviewer keys on a host the agent can't
  reach. A process that can write and sign a decision can approve its own change.
  HMAC keys are shared secrets: in production, have reviewers sign with a key
  the gate can only verify, or take the reviewer's identity from your identity
  provider.
- Serve both servers over `https://`; bearer tokens over plain HTTP cross the
  network readable.
- Set each client's tool timeout above `GATE_TIMEOUT`: the plugin sets 300,000
  ms for `change-gate`; OpenCode's `timeout` takes the same value.
- When you publish, make the plugin entry a `git-subdir` source with `ref` and
  `sha` (Chapter 7); a relative-path entry like the one here can't be pinned.
