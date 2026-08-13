# Appendix B: AGS with Loro and MagAgent

The command and code snippets from Appendix B. This appendix demonstrates two
harnesses the author built that implement the Agentic Graph Specification (AGS)
from Appendix A: MagAgent, a terminal-native developer harness, and Loro, an
enterprise harness.

## MagAgent, the terminal-native harness

### Starting a session

```bash
magent ask "..."              # one-shot task
magent                        # interactive session
magent doctor                 # setup check
magent tools doctor           # optional capability check
magent memory ...             # the MagGraph memory graph
magent context map            # memory, workbench, and project state together
```

### The graph lifecycle

```bash
magent graph generate "repair the failing API tests" --project . --out repair.agraph.yaml
magent graph validate repair.agraph.yaml --strict
magent graph plan repair.agraph.yaml
magent graph run repair.agraph.yaml --project .
magent graph status <run-id>
magent graph resume <run-id>
```

Review the generated document before running it. The documentation says to
review or edit the generated graph, validate it again, and then run it, and that
`--yes`, which approves every gate and checkpoint, should not be used for an
untrusted graph.

### MagGraph memory

MagAgent's memory is a versioned Markdown graph read through the `maggraph`
Python package.

```python
import maggraph

config = maggraph.load_config("maggraph.toml")
index = config.open_index()

index.list_nodes()
node = index.read_node("welcome")
node.body, node.links, node.node_type
```

### Generating the MCP server

MagGraph generates its own MCP server from the graph's schema:

```bash
maggraph scaffold --mcp --skill --output ./agent --config maggraph.toml
```

That produces a FastMCP server wired to the package, its requirements, a README,
and a `SKILL.md` carrying the machine-readable graph schema and operation
documentation. It is the server-and-skill pairing from Chapter 9, produced
automatically rather than written by hand.

Run it:

```bash
pip install maggraph fastmcp
export MAGGRAPH_CONFIG="/absolute/path/to/maggraph.toml"
python agent/mcp_server/server.py
```

## Loro, the enterprise harness

### Setup

```bash
python -m pip install loro-agent
loro configure
loro config check --strict
loro doctor
```

The setup wizard offers a `mock` provider so you can verify the CLI,
configuration loading, memory paths, artifact folders, and health checks before
connecting a paid provider.

### Running graphs

```bash
loro graph generate "Create a release readiness report" --out release.agraph.yaml
loro graph validate release.agraph.yaml --strict
loro graph plan release.agraph.yaml --json
loro graph run release.agraph.yaml --dry-run
loro graph run release.agraph.yaml --params '{"release":"0.3.0"}'
loro graph status RUN_ID
loro graph resume RUN_ID
```

Loro pins its implementation to a specific upstream specification commit and
vendors the graph schema, the run-record schema, and the reference validator, so
validation stays reproducible across installations and over time.
