# Agent benchmark

`eval/run_agents.py` in Claude Code 2.1.316 (`claude-opus-5-5`) and OpenCode 1.19.5
(`openai/gpt-6.1-sol`), each session in an empty folder with built-in tools off and one MCP server:
`search_docs` (`eval/chunk_server.py`) or the three traversal tools (`graph/server.py`). Every
question twice per harness and side.

## `final/` (160 sessions)

Questions as in `eval/questions.jsonl`: multi-hop questions state their scope and are closed-set.
The vector-side single-hop sessions are from the first pass (the single-hop questions and the
`search_docs` tool did not change); all other sessions ran with the current questions and tools.
Graded by `eval/grade.py` with `claude-sonnet-5-5`; each verdict is in `<session>.judge3.json`
(`included` per expected item, `extra` items of the asked-for kind given as part of the answer).
`<session>.json` holds the answer, tool calls, token totals, and Claude Code's reported cost.

| Harness | Retrieval | Single-hop | Multi-hop | Recall | Precision | Calls | Input tokens | Cost |
|---|---|---|---|---|---|---|---|---|
| Claude Code | Vector search | 20/20 | 20/20 | 1.00 | 1.00 | 4.5 | 19,787 | $0.0758 |
| Claude Code | Graph traversal | 14/20 | 18/20 | 1.00 | 0.98 | 2.4 | 13,462 | $0.0464 |
| OpenCode | Vector search | 20/20 | 18/20 | 0.99 | 0.99 | 4.2 | 6,900 | n/a |
| OpenCode | Graph traversal | 14/20 | 18/20 | 1.00 | 0.98 | 1.2 | 2,926 | n/a |

Fully correct out of 20; the other columns are means per multi-hop question. OpenCode reports a cost
of 0 under its sign-in. Multi-hop answers not fully correct: q11 and q17 graph sessions listing
PaymentsAPI or OrdersAPI among affected services (one run each per harness), q17 OpenCode vector run
1 (OrdersAPI), q20 OpenCode vector run 2 (recall 7/9). Graph single-hop: q02, q03, q04, q06, q07,
q08, q10 fully correct in every session (q02 through the source sentence on the `RETRY_ATTEMPTS`
edge); q01 and q05 half; q09 none.

A stricter first version of the judge prompt, which counted any other entity the answer named,
scored multi-hop full answers at 7/20 (vector) and 12/20 (graph); a hand check of three answers it
failed showed it counting background and excluded entities, so the prompt was narrowed to items of
the asked-for kind presented as answers.

## `four-types/` (80 sessions, graph side only)

An earlier graph with four relationship types (no `EXPOSES`), earlier question wording, and an
earlier `find_dependents`, graded with `--regex`. With no service-to-API link, q14 and q19 had no
traversal. Claude Code answered both by assuming from the names that each service serves the API
named after it, and in `claude-graph-q19-run1` said the graph lacked that link; OpenCode answered q19
"nothing depends on PaymentsService" in both runs.

## `loose-wording/` (16 sessions)

q11 and q15 as first worded, without a hop limit ("Which services break if the NotificationsAPI
changes its retry semantics?"). On q11 all four vector-search sessions named only the two direct
callers. The four graph sessions (earlier `find_dependents`, which also listed APIs) asked for four
hops and named six to eight services and APIs. On q15 both Claude Code vector sessions narrowed the
answer to ApiGateway; both OpenCode vector sessions listed PaymentsService and left out BillingService
and ReportingService.
