# Incremental refresh

On a copy of `docs/` and `graph/extractions/` (pointed at with `GRAPH_DOCS`, `GRAPH_CACHE`,
`GRAPH_DB`): built the graph (`0-build.txt`), added one sentence to billing-service.md
(`billing-service.edited.md`), deleted search-service.md, and ran `python3 extract.py --model`.

| Step | Result |
|---|---|
| Refresh (`1-refresh.txt`) | 1 updated, 1 removed, 8 unchanged; 1 model call, $0.0152; 26 nodes, 29 edges (from 27 and 30) |
| `query.py dependents PaymentsAPI 1` (`2-query.txt`) | OrderService, RenewalsWorker, BillingService |
| SearchService node (`3-search-node.txt`) | Still present with 0 edges, mentioned by api-gateway.md |
| `query.py edge BillingService PaymentsAPI` (`4-edge.txt`) | The new edge with its sentence and document |

`billing-reextracted.json` is the new extraction. `eval/check_refresh.py` checks the patching
logic without a model.
