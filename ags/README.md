# Appendix A: The Agentic Graph Specification (AGS)

| Path | What it is |
|---|---|
| `migrate-order-service.agraph.yaml` | Chapter 5's execution graph (`ch05-subagents/nodes/` and `run-graph.sh`) for the `order-service.js` migration, written as an AGS 1.0 document |

Validate it with the reference validator from PyPI:

```bash
python3 -m pip install agentic-graph-spec==1.0.4
ags-validate --strict ags/migrate-order-service.agraph.yaml
```

Expected output ends with `1 document(s): 0 error(s), 0 warning(s)`. `--strict` exits with
code 2 on a warning and 1 on an error, so it works as a CI step.

The graph's success criteria are the checks `run-graph.sh` runs between nodes, plus
`no_db_import`, which `run-graph.sh` lacks: `grep -n db.js src/services/order-service.js` with
`expect_exit_code: 1` passes only once the module no longer imports `../db.js`, so an agent that
changes nothing can't pass the node. The `run` field is not a template, so the module path is
written out; migrating several modules needs one node per module, or a `map` node at
conformance level 3.

The canonical digest is the same in every implementation that was checked on 2026-11-05
(reference Python library 1.0.4, MagAgent 1.4.0, Loro 0.22.0), and for a JSON copy of the file:
`sha256-5XVb3axq6g9HuExsesW5zrcZKeBd53y+D8e7xNFadiI=`. Editing the file changes it.

Appendix B runs this graph in MagAgent and Loro; see
`../appendix-b-loro-magagent/runs/2026-11-05-ags-walkthroughs/`.
