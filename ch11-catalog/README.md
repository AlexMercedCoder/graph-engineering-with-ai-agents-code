# Chapter 11: Bridging the Governance Gap with Semantic Layers

A semantic layer over a ten-table insurance warehouse, a lineage validator, and a
governed-data MCP server with three tools under two scopes. Everything runs locally
on SQLite; no accounts, no Docker, no commercial license.

## Setup

```
pip install -r requirements.txt     # PyYAML and the MCP Python SDK 2.x (tested with 2.0.0)
python3 warehouse/seed.py           # writes warehouse/warehouse.db (fixed seed)
bash eval/checks.sh                 # the deterministic checks the chapter shows
```

The seed is fixed, so every number in the chapter should match yours to the cent.
`warehouse.db` is generated, not committed.

## What's here

| Path | What it is |
|---|---|
| `catalog.yaml` | The semantic layer: six datasets, five relationships, seven dimensions, five metrics with bindings and lineage, an AI context block, and the `not_modelled` list |
| `validate.py` | `Catalog` (search, resolve, the four lineage checks), `compile_to_sql`, `format_rejection`, and a command line |
| `warehouse/seed.py` | Builds the ten-table warehouse; `--schema` prints the table definitions |
| `warehouse/policies.yaml` | The access policies the data platform enforces per identity |
| `warehouse/dataplatform.py` | Stand-in for the data platform: builds each identity a connection holding only what its policy grants, read-only, with a row cap and a timeout |
| `server/tools.py` | `navigate_catalog`, `generate_governed_sql`, `execute_query` as plain functions |
| `server/server.py` | The MCP server (`MCPServer` from SDK 2.x), registering tools by granted scope |
| `server/cli.py` | The same three operations from a shell, for harnesses without MCP |
| `skills/answer-with-governed-data/SKILL.md` | The skill that pairs with the server |
| `eval/questions.jsonl` | Six business questions: four answerable, one not modelled, one restricted |
| `eval/truth.py` | Expected answers from hand-written SQL; `--check` compares them with compiled SQL |
| `eval/grade.py` | Scores a Claude Code or OpenCode transcript against `truth.py` |
| `eval/run-agents.sh` | Runs one harness in one setup (raw, catalog, tools, skill) in a fresh folder |
| `eval/checks.sh` | The deterministic checks: compile, refuse, the four checks, identity, signatures, scopes, row cap |
| `runs/` | Published runs, sanitized |

## The warehouse

Ten tables. The catalog models six. The other four are what real warehouses accumulate:
`fct_premiums_v1` (a legacy snapshot), `stg_premium_raw` (a staging copy in which recent
rows appear twice), `dim_policyholder` (names and email addresses), and `dim_date`.
`fct_policy_premium` has two amount columns (`premium_amt`, which finance means, and
`premium_amt_gross`, which includes taxes and fees) and two paths to a region (its own
`geo_id`, and `agent_id` through the agent's office). About a fifth of its rows are quotes.

## Identities and scopes

The server reads `CATALOG_IDENTITY` (`analyst`, `emea-analyst`, `finance`; anything else
sees nothing) and `CATALOG_SCOPES` (`catalog:read`, `data:read`) from its environment.

- `analyst` can't see `commission_paid` or its table, or policyholder names and emails.
- `emea-analyst` is an analyst whose premium rows are limited to EMEA.
- `finance` sees everything.
- Without `data:read`, the server doesn't register `execute_query` at all.

Over HTTP, identity and scopes would come from the verified access token (Chapter 9).

## Registering the server

Claude Code, without touching your user configuration:

```
cat > mcp.json <<'JSON'
{"mcpServers": {"governed-data": {"command": "python3", "args": ["<path>/ch11-catalog/server/server.py"],
  "env": {"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}}}}
JSON
claude --mcp-config mcp.json --strict-mcp-config
```

OpenCode, in the project's `opencode.json`:

```json
{"mcp": {"governed-data": {"type": "local",
  "command": ["python3", "<path>/ch11-catalog/server/server.py"],
  "environment": {"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}}}}
```

Copy `skills/answer-with-governed-data` into `.claude/skills/` to add the skill (OpenCode
reads that folder too).

## Command line

```
python3 validate.py --list
python3 validate.py --metric net_written_premium --dimensions region --range 2026-Q3
python3 validate.py --sql-file my-query.sql
CATALOG_SCOPES="catalog:read data:read" python3 server/cli.py ask net_written_premium region 2026-Q3
```

`validate.py` parses SQL with regular expressions to stay dependency-free. It handles FROM
lists with comma joins, JOIN clauses, aliases, and quoted table names, and checks qualified
column references only. Treat it as advisory until it runs on a real parser such as sqlglot;
enforcement belongs to the data platform.

`server/cli.py` reads identity, scopes, and `CATALOG_SIGNING_KEY` from its environment, so an
agent with a shell can change all three for its own commands. Don't hand the CLI to an agent
as a boundary unless a wrapper fixes its environment out of the agent's reach (for example,
running as another OS user); use the MCP server, whose environment the harness sets.

## Agent runs

```
bash eval/run-agents.sh claude raw   runs/mine/claude-raw-1.jsonl
OPENCODE_MODEL=openai/gpt-6.1-sol bash eval/run-agents.sh opencode skill runs/mine/oc-skill-1.jsonl
python3 eval/grade.py runs/mine/*.jsonl
```

The chapter's results are in `runs/2026-11-03-governed-access/`, and the deterministic
check output in `runs/2026-11-03-checks/`.
