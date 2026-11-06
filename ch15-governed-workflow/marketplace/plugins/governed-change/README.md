# governed-change

Change a deployed service configuration from evidence. Production changes wait
for a reviewer with the payments-oncall role, who reads an approval packet the
change gate builds from the evidence and the service graph.

The plugin carries three skills, an audit hook, and the addresses of two
servers it doesn't contain: `project-knowledge` and `change-gate`. Set
`GOVERNED_KNOWLEDGE_TOKEN` and `GOVERNED_GATE_TOKEN` in the environment you
start Claude Code from; the plugin holds no credentials. Before you publish the
marketplace, replace the `127.0.0.1` addresses in `.mcp.json` with your
deployed servers.
