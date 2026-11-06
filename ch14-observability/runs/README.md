# Chapter 14 runs, 2026-11-05

Claude Code 2.1.316 with `claude-opus-5-5`, and OpenCode 1.19.5 with `openai/gpt-6.1-sol`,
both exporting to `collector.py`. Every folder holds `telemetry/` (spans, events, metrics),
`transcript.jsonl`, `server-stderr.txt`, `run.json`, and `triage.json`. The matrix ran on MCP
Python SDK 2.0.0 with the collector's `--keep-content` (development mode, synthetic graph).

Published copies are sanitized with `tools/sanitize-run.py`: spans of the node kinds
`graphspans.py` reads, plus OpenCode's `ai.toolCall`, keep their attributes without prompt,
response, or tool content (the skill name a `skill` call loaded is kept as
`ai.toolCall.skill`); every other span keeps only its IDs, name, and times, so trees still
join up; `user.id` and `session.id` are hashed wherever they appear; OpenCode's operational
logs and Claude Code's plugin, settings, prompt, and response events are dropped; local
paths, email addresses, and the username are replaced. The collector had already hashed
`user.email`, account IDs, and the organization ID. Span, event, and byte counts quoted in
the chapter (23 spans, 19 events, about 60 KB for a Claude Code session; 1,197 spans and about
830 KB for OpenCode) were measured on the collector's output before sanitizing; the span
counts survive sanitizing, the event counts and sizes don't.

## `2026-11-05-triage/`: the regression matrix

`bash eval/run-matrix.sh runs/2026-11-05-triage 3`, three sessions per condition per harness,
36 in all. `verdicts.json` pins each run's verdict for `eval/check-saved-runs.py`.

| Harness | Condition | Runs | Verdicts | Answer correct | Mean tokens (in / cache read / out) |
|---|---|---|---|---|---|
| claude | baseline | 3 | 3 pass | 3 of 3 | 453 / 125,727 / 1,016 |
| claude | bad-description | 3 | 3 execution graph | 3 of 3 | 428 / 93,787 / 872 |
| claude | depth-cap-silent | 3 | 3 knowledge graph | 0 of 3 | 287 / 125,726 / 698 |
| claude | depth-cap | 3 | 3 knowledge graph | 2 of 3 | 566 / 191,585 / 1,598 |
| claude | soft-body | 3 | 1 pass, 2 reasoning | 1 of 3 | 415 / 125,725 / 1,176 |
| claude | stale-rule | 3 | 3 reasoning | 0 of 3 | 400 / 125,815 / 896 |
| opencode | baseline | 3 | 3 pass | 3 of 3 | 7,412 / 4,864 / 242 |
| opencode | bad-description | 3 | 3 execution graph | 3 of 3 | 4,469 / 3,584 / 175 |
| opencode | depth-cap-silent | 3 | 3 knowledge graph | 0 of 3 | 6,028 / 6,144 / 166 |
| opencode | depth-cap | 3 | 3 knowledge graph | 0 of 3 | 4,782 / 7,424 / 177 |
| opencode | soft-body | 3 | 3 pass | 3 of 3 | 6,043 / 6,229 / 324 |
| opencode | stale-rule | 3 | 3 reasoning | 0 of 3 | 3,203 / 9,131 / 228 |

Token columns are means per session: fresh input, cache reads, output. Claude Code's
cost per session (from `api_request` events): baseline $0.106 each run; bad-description
$0.095 to $0.097; depth-cap $0.158 and $0.156 for the two sessions that walked the graph
hop by hop and $0.103 for the one that didn't.

Reading the conditions:

- `bad-description`: no session loaded the skill; every agent called `find_dependents` on its
  own and answered correctly. The triage fails them on the route.
- `depth-cap-silent`: every session reported three services and none said the list could be
  incomplete; three Claude Code answers said the search found nothing further out.
- `depth-cap`: with the server's partial-coverage line, two Claude Code sessions called
  `find_dependents` on each dependent (8 calls) and reached all seven services; the third
  Claude Code session and all three OpenCode sessions reported three and said the list was
  incomplete. In one of the two walking sessions the prose said "Eight services" while the
  `Affected services:` line listed the correct seven.
- `soft-body`: two of three Claude Code sessions followed the softened step and listed only
  the direct dependents; all three OpenCode sessions listed all seven.
- `stale-rule`: all six sessions left ApiGateway and AuditService out, and all six said so in
  a sentence.

## `2026-11-05-access/`

The same harness setup with the question "Which services read the PAYMENT_API_KEY
configuration key?", twice per harness per role. `contractor` sessions use the token without
`config:read`; `sre` sessions the token with it. `python3 policy.py access runs/2026-11-05-access/*`
prints the decisions: four denials for `contractor-7`, four allows for `sre-oncall`. The triage
verdicts in these folders don't apply, since the question isn't the blast-radius question.

## `2026-11-05-budget/`

`--max-budget-usd` at $0.05, $0.08, and $0.20, once each. The first two ended with
`error_max_budget_usd` and exit code 1, after $0.067 and $0.093; the $0.20 session finished
at $0.107. Exit codes were read from the shell at the time and aren't stored in the folders.
The $0.05 and $0.08 folders were sanitized by an earlier version of the sanitizer that dropped
non-node spans, so their trees don't join up; only their transcripts are used.

## `2026-11-05-notrace/`

`bash eval/run-notrace.sh`, twice: no telemetry, `hooks/audit-trace.sh` (Chapter 6's hook with
`agent_id` and the skill name), and the server's `GRAPH_AUDIT_LOG`. Both sessions logged Skill,
ToolSearch, and the MCP call, and the server logged 7 paths with complete coverage.

## `2026-11-05-sdk-2.3/`

The baseline and depth-cap conditions once per harness on MCP Python SDK 2.3.0, after the
advisories for releases before 2.2.0: same verdicts as the matrix (pass, pass, knowledge
graph, knowledge graph), and the same trace-context behavior (header from Claude Code, none
from OpenCode).

## `2026-11-05-production-collector/`

`COLLECT=production bash eval/run.sh ... baseline`, once per harness: the collector without
`--keep-content` and with `--agent-spans-only`. Both triaged as pass; the OpenCode tree joins
up through the skeleton spans and the skill name survives. OpenCode's spans file was 486 KB.

## `2026-11-05-bench/`

`python3 tools/bench-overhead.py` three times, with the collector running.

## `2026-11-05-project-settings/`

`project-settings.json` put the telemetry variables (and `OTEL_LOG_USER_PROMPTS=1`, endpoint
port 8834) in a project's `.claude/settings.json`, with none in the shell, and a collector
listened on 8834. One session; the collector received nothing (the empty `telemetry/` folder).
`bash eval/check-project-settings.sh` repeats the test and printed
`records received from project settings: 0`.

## `2026-11-05-incomplete/`

Sessions set aside and rerun. Three matrix sessions and the first four Claude Code access
sessions ended with `api_error` (Claude Code) or with no final reply (OpenCode); the triage now
marks such a session `incomplete` instead of giving it a class. A later batch of three matrix
sessions ran after the eight-hour test tokens expired, so the graph server refused them with
401; those were deleted and rerun after `eval/run.sh` learned to renew expired tokens. Note
that the triage called those three "execution graph": the tool never ran, which is true of
the route and says nothing about the cause.

An earlier version of the matrix (before the skill ended answers with an `Affected services:`
line) graded answers by every service name in the prose. It scored the stale-rule sessions as
passes, because each answer named the two services in the sentence that explained leaving them
out. Those runs aren't published; the line and its parser replaced that check.

