# Chapter 13: Bridging the Developer-Analyst Divide

Chapter 13 takes the Chapter 11 governed-data tools and skill from the terminal
to Claude Desktop's Chat and Cowork, where analysts work. It builds three
things: a plugin that carries the skill and names the connector, a remote
connector that takes identity from an OAuth access token, and, for contrast, a
desktop extension (`.mcpb`) of the same server.

Everything except the last step runs on your machine. Adding the connector in
Claude Desktop needs the server on a public HTTPS address (or behind an MCP
tunnel), a paid plan, and someone to sign in from the app.

## Setup

```
pip install -r ../ch11-catalog/requirements.txt    # PyYAML and the MCP Python SDK 2.x (tested 2.0.0 and 2.3.0; use 2.2.0+ in production)
python3 ../ch11-catalog/warehouse/seed.py          # the warehouse the connector serves
python3 connector/server.py                         # http://127.0.0.1:8813/mcp, leave it running
python3 tools/connector-check.py                    # in a second terminal: expect "all checks pass"
```

The bundle needs Node.js (for `npx`) and uv; the agent runs need Claude Code or
OpenCode.

## What's here

| Path | What it is |
|---|---|
| `connector/server.py` | The Chapter 11 tools over Streamable HTTP, with identity and scopes read from the verified access token, resource metadata that lists both scopes, and an access line on every query result |
| `connector/authserver.py` | A test OAuth 2.1 authorization server on the same origin (DCR, S256 PKCE, resource binding, refresh rotation) with a consent page that stands in for single sign-on |
| `tools/connector-check.py` | Signs in the way Claude's hosted apps do and checks each requirement; `--token <user>` prints an access token for the agent runs |
| `tools/latency.py` | Times `execute_query` over stdio and over the connector |
| `marketplace/` | A plugin marketplace an organization can sync: `.claude-plugin/marketplace.json` and `plugins/governed-data/` (manifest, `.mcp.json`, skill, README) |
| `bundle/` | `manifest.json` and `pyproject.toml` for a uv-type MCP Bundle, `build.sh` to pack it, `run-bundle.py` to start it over stdio the way Claude Desktop does |
| `eval/run-agents.sh` | Chapter 11's six questions through the connector, signed in as one identity, with the plugin's skill |
| `runs/` | Published runs, sanitized |

## Test identities

The consent page offers four sign-ins. The data platform policies are Chapter 11's
`warehouse/policies.yaml`.

| Sign in as | Identity the platform sees | Scopes |
|---|---|---|
| `analyst` | analyst | `catalog:read data:read` |
| `emea-analyst` | emea-analyst (premium rows limited to EMEA) | `catalog:read data:read` |
| `finance` | finance (sees commission) | `catalog:read data:read` |
| `new-analyst` | analyst | `catalog:read` only |

Tokens expire after an hour and live in the server's memory, so restarting the
server signs everyone out.

## Running the agents

```
bash eval/run-agents.sh claude analyst runs/mine/claude-analyst-1.jsonl
OPENCODE_MODEL=openai/gpt-6.1-sol bash eval/run-agents.sh opencode emea-analyst runs/mine/opencode-emea-1.jsonl
```

Claude Code loads the plugin with `--plugin-dir` and reaches the connector through
`--mcp-config` with a bearer token, so the plugin's placeholder URL is never used.
The token goes into a temporary folder that the script deletes on exit; don't
commit a configuration file with a token in it. `runs/mine/` is ignored by Git.

## Packaging

```
claude plugin validate marketplace --strict
claude plugin validate marketplace/plugins/governed-data --strict
(cd marketplace/plugins && zip -r ../../governed-data.zip governed-data)   # for Customize > Plugins > Upload plugin
bash bundle/build.sh                                                      # bundle/governed-data-local.mcpb
python3 bundle/run-bundle.py bundle/governed-data-local.mcpb finance
```

Before an organization syncs `marketplace/`, change the URL in
`plugins/governed-data/.mcp.json` to your connector's HTTPS address. Organization
sync requires the marketplace repository to be private or internal.

## What still needs the app

- Deploy `connector/` behind HTTPS with your identity provider in place of
  `authserver.py`. The test server's `load_access_token` is also the connector's
  token check, so write a token verifier that checks signature, issuer,
  audience, and expiry, map the provider's subject to a platform identity, and
  change `ISSUER` and `RESOURCE`. MCP tunnels, for servers in a private network,
  are an Enterprise research preview.
- Add it under **Customize > Connectors** (an Owner adds it under **Organization
  settings > Connectors** on Team and Enterprise), and sign in.
- Upload the plugin zip, or sync the marketplace from **Organization settings >
  Plugins & skills** and set its default access.
- Ask a question in Chat and in a Cowork task, and compare the answer with the
  table in `runs/README.md`.
