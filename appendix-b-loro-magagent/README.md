# Appendix B: AGS with Loro and MagAgent

Commands and configuration from Appendix B, which runs the Agentic Graph Specification (AGS) in
MagAgent and Loro, the two harnesses that publish level 3 results, and uses MagGraph as memory
from any MCP client. Versions used: MagAgent 1.4.0, Loro 0.22.0, MagGraph 0.4.1
(2026-11-05). The runs are in `runs/2026-11-05-ags-walkthroughs/`; its README lists every result.

Run graphs with command criteria only in a disposable copy of a project.

## MagAgent

```bash
python3 -m pip install "mag-agent[mcp]"     # the mcp extra avoids "No module named 'mcp'" with LiteLLM 1.108.0
magent user create reader
magent provider set mock                     # offline; no model is called
mkdir -p ~/.config/magent/skills
cp -r ch04-routing/skills/migrate-module ~/.config/magent/skills/
magent mode silent                           # in 1.4.0, balanced mode denies the node criteria under --yes
```

Then, in a fresh copy of `sample-project/`:

```bash
magent graph validate ../ags/migrate-order-service.agraph.yaml --strict
magent graph plan ../ags/migrate-order-service.agraph.yaml
MAGENT_MOCK_SCRIPT=../appendix-b-loro-magagent/runs/2026-11-05-ags-walkthroughs/inputs/mock-claims-done.json \
  magent graph run ../ags/migrate-order-service.agraph.yaml --project . --yes
magent graph status <run-id> --json
magent graph resume <run-id>
```

Swap in `mock-replay.json` for the passing run. Set the mode back with `magent mode balanced`.

## Loro

```bash
python3 -m pip install loro-agent
loro configure --provider mock --model mock --no-discover-models
loro config check --strict
loro doctor
loro graph validate ../ags/migrate-order-service.agraph.yaml --strict   # LP006 by default
```

To accept command criteria in one project, add to `.loro/config.local.toml`:

```toml
[agraph]
allow_command_criteria = true
```

The gate test uses `runs/2026-11-05-ags-walkthroughs/loro/gate-only.agraph.yaml`:

```bash
LORO_IDENTITY_ROLES=maintainer loro graph run gate-only.agraph.yaml --yes
```

A role read from the environment is self-asserted. For a real deployment, managed configuration
should set `environment_enabled = false` under `[identity]` and `allow_non_interactive = false`
under `[approvals]`.

## MagGraph

```bash
python3 -m pip install maggraph fastmcp
# The maggraph CLI comes from the GitHub release binaries, or:
#   git clone https://github.com/AlexMercedCoder/MagGraph && cd MagGraph
#   cargo install --path maggraph-cli --features maggraph/ui
maggraph scaffold --mcp --skill --output ./agent --config maggraph.toml
mkdir -p agent/maggraph-skill
mv knowledge_graph/SKILL.md agent/maggraph-skill/SKILL.md   # in 0.4.1, SKILL.md in the graph root breaks the index
export MAGGRAPH_CONFIG="/absolute/path/to/maggraph.toml"
python3 agent/mcp_server/server.py
```

`runs/2026-11-05-ags-walkthroughs/maggraph/` has the four-node example graph and the
`mcp.json` (Claude Code) and `opencode.json` (OpenCode) files that connect the server with its
write tools removed.
