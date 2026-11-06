# Chapter 13 runs, November 5, 2026

Local paths are replaced with `<repo>`, `<run-dir>`, or `<path>`. Claude Code
transcripts keep assistant, user, and result events only. Access tokens came
from the test authorization server, lived in memory for an hour, and were never
written into a transcript.

## 2026-11-05-connector

`tools/connector-check.py` against `connector/server.py` on 127.0.0.1:8813, MCP
Python SDK 2.0.0.

| File | What it shows |
|---|---|
| `check-pass.txt` | All 19 checks pass: discovery as Claude's client performs it, sign-in with PKCE and the claude.ai callback, what four identities get, audience refusal, refresh rotation |
| `check-sdk-default-metadata.txt` | The same check against the server without `advertise_all_scopes`: the SDK lists only `catalog:read` in the resource metadata, the client requests only that, and 6 of 19 checks fail because no analyst can run a query |
| `latency.txt` | `tools/latency.py 50`, twice: median per `execute_query` call 24.9 and 29.6 ms over stdio, 28.8 and 30.3 ms over the HTTP connector on loopback |

## 2026-11-05-bundle

`bundle/build.sh` with `@anthropic-ai/mcpb` 2.1.2 (`Manifest schema validation
passes!`), then `bundle/run-bundle.py`, which starts the packed bundle over
stdio as Claude Desktop would. uv resolved the SDK from `mcp>=2,<3`.

| File | What it shows |
|---|---|
| `run-analyst.txt` | Identity setting `analyst`: net written premium 1,243,284.20; commission rejected |
| `run-finance.txt` | Identity setting `finance`, typed by whoever installs the bundle: commission paid 98,224.12 |
| `archive-listing.txt` | The bundle carries `warehouse/warehouse.db`, including `fct_commissions` (1,988 rows) |

## 2026-11-05-plugin

| File | What it shows |
|---|---|
| `validate.txt` | `claude plugin validate --strict` passes for the marketplace and for the plugin (Claude Code 2.1.316); two directory-only warnings (no icon, no privacy URL) don't apply to an organization plugin |
| `details.txt` | `claude plugin details`: the skill costs about 120 tokens in every session and about 330 when it fires (Claude Code's estimate) |

## 2026-11-05-agents

`eval/run-agents.sh`: Chapter 11's six questions, through the connector, with the
plugin's skill. Claude Code 2.1.316 with `claude-opus-5-5`; OpenCode 1.19.5 with
`openai/gpt-6.1-sol`. Graded with `../ch11-catalog/eval/grade.py`.

The current version of `connector/server.py` ends every `execute_query` result
with an access line naming the signed-in identity and any row limits, and step 8
of the skill reports it. `grades.txt` has the grader's output.

| Identity | Harness | Runs | Result |
|---|---|---|---|
| analyst | Claude Code | 2 | 6/6, 6/6 |
| analyst | OpenCode | 2 | 6/6, 6/6 |
| emea-analyst | Claude Code | 2 | EMEA figures match the EMEA-scoped truth in both and both open by saying access covers EMEA only; run 1 marks q1 to q3 REFUSED as not company-wide and gives the EMEA figures in the reason, run 2 answers with the EMEA figures |
| emea-analyst | OpenCode | 2 | EMEA figures match in both; both say the figures are EMEA-only, not company-wide |
| new-analyst (`catalog:read` only) | Claude Code | 1 | q1 to q4 refused, naming the missing `data:read` scope and the data team |
| new-analyst | OpenCode | 1 | Same |

The grader scores emea-analyst q1 to q3 as wrong or refused because it expects
company-wide figures; the EMEA-scoped truth is: net written premium 2026-Q3 EMEA
343,269.84; gross written premium H1 2026 Auto 134,856.74, Commercial 395,649.19,
Home 154,709.40; policies written March 2026, 27; claims paid Q2 2026 by severity
unchanged (the row policy covers premium rows only).

No final session names `fct_commissions` or any other table the identity can't see.

Session cost: Claude Code reported $0.19 to $0.23 per session at API prices and
about 203,000 to 206,000 input tokens, most of it cached harness context;
OpenCode used 43,500 to 45,000 input tokens per session.

### Earlier versions

`v1/`: the connector without an access line, and the skill without it in step 8.
Two analyst sessions per harness, one emea-analyst and one new-analyst session
per harness. Analyst results were the same, 6/6 in all four. For emea-analyst,
Claude Code wrote "This is probably EMEA only" and "I can't tell whether your
access limits these to EMEA"; OpenCode wrote "not necessarily company-wide
totals".

`v2/`: an access line that also listed the identity's hidden tables and columns
("hidden from you: fct_commissions, ..."). Scoping was stated in all four
emea-analyst sessions, and all eight analyst and emea-analyst sessions repeated
the name `fct_commissions` back to the user, which Chapter 11's catalog keeps
from an analyst. The final line names row limits only.

Input tokens, analyst sessions: Claude Code averaged 204,687 (v1) and 204,562
(final); OpenCode 43,923 (v1) and 44,703 (final). OpenCode's new-analyst sessions in `v1/` and the final set,
which never receive an access line, differed by 14,530 tokens, so the
780-token difference is inside run-to-run variation.
