# Chapter 12 runs, 2026-11-05

Claude Code 2.1.316 (`claude-opus-5-5` for sessions; `claude-haiku-5-5` for the model
classifier and the retrieval worker; `claude-sonnet-5-5` as judge) and OpenCode 1.19.5
(`openai/gpt-6.1-sol`). Transcripts have the `init` and rate-limit events removed and local
paths replaced with `<run-dir>`, `<repo>`, `<scratch>`, or `<home>`.

| Folder | What it holds |
|---|---|
| `2026-11-05-routing/final-rules/` | `route_eval.py` with the rules as committed: rules only, two passes with the model fallback, two model-only passes, and the rule latency |
| `2026-11-05-routing/earlier-rules/` | Two more passes of each model setup, made before the clause split and the `how long` / `what happens` vector words were added. Those changes touch only questions the rules already matched, so the nine unmatched questions, and the model's answers to them, are the same population |
| `2026-11-05-benchmark/` | Chapter 10's twenty questions, twice per harness, `routed` and `free` (160 sessions), with judge verdicts (`*.judge3.json`) |
| `2026-11-05-combined/` | The four combined questions, twice per harness, `vector`, `graph`, and `routed` (48 sessions), with judge verdicts (`*.judge.json`) |
| `2026-11-05-subcycle/final/` | The brief task, three runs per setup and harness, with the worker as printed (step 5 calls `check_evidence`): transcript, `brief.md`, and summary |
| `2026-11-05-subcycle/without-check/` | Three Claude Code runs per setup with the worker's instructions minus step 5. `claude-worker-run3` returned 17 evidence documents without `cost_tokens` |
| `2026-11-05-act/` | The two act tasks, twice per harness with the worker: transcript, `brief.md`, the edited `payments.conf`, and `grade.txt` |
| `2026-11-05-routing/vector-probes.txt` | `eval/vector_probes.py` output behind the `search_docs` confidence thresholds |
| `2026-11-05-subcycle/parallel-workers/` | A Claude Code run in which the main session started six workers at once; three lost `search_docs` calls to `Connection closed` when the first worker exited. After this run the worker's description asks for one call per task |

The worker was named `retrieval-router` in these runs and is `retrieval-worker` now; the
definition is otherwise the same, except that its description gained "sending all of a task's
questions in one call" after the parallel-workers run. The breakdown rule in `router.py` was
narrowed (it now needs a business figure before `by region` and the like) after the routing
passes; `final-rules/rules-after-breakdown-fix.txt` shows the same 36/42 and no labeled question
routed differently. The act runs passed the worker with `agents/build_agents_json.py`; the brief
runs passed the same definition as a file. An `mcpServers` entry in the agent file itself did not
start the server in Claude Code 2.1.316 (four variants tried), which is why the chapter uses
`--agents`.

## Results

Routing (42 questions): rules only 36; rules then `claude-haiku-5-5` 42, 40, 42, 42; model
only 39, 40, 42, 41.

Chapter 10's questions (fully correct single-hop / multi-hop out of 20; means per question):

| Harness | Setup | Single-hop | Multi-hop | Calls | Input tokens | Cost |
|---|---|---|---|---|---|---|
| Claude Code | All four tools, no router | 20/20 | 20/20 | 3.2 | 14,026 | $0.047 |
| Claude Code | Routed | 20/20 | 20/20 | 2.0 | 11,566 | $0.041 |
| OpenCode | All four tools, no router | 20/20 | 19/20 | 1.8 | 3,657 | n/a |
| OpenCode | Routed | 20/20 | 18/20 | 1.2 | 2,664 | n/a |

Vector-only and graph-only baselines are Chapter 10's runs, same versions, 2026-11-03.

Combined questions: graph only 0/8 in both harnesses (every service, never the fact); vector
only and routed 8/8 in both.

Brief task (means of three runs):

| Harness | Retrieval | Correct | Main requests | Main input tokens | Largest request | Worker input tokens | Time | Cost |
|---|---|---|---|---|---|---|---|---|
| Claude Code | Inline | 18/18 | 8.0 | 122,512 | 22,303 | none | 74 s | $0.342 |
| Claude Code | Worker | 18/18 | 3.0 | 40,944 | 17,443 | 58,191 | 101 s | $0.223 |
| OpenCode | Inline | 18/18 | 9.0 | 110,723 | 16,397 | none | 107 s | n/a |
| OpenCode | Worker | 18/18 | 4.3 | 52,023 | 14,885 | 26,417 | 187 s | n/a |

All 125 evidence documents in the final briefs pass `evidence.py check`.

Act tasks: `act_fix` 4/4 (each set `AUTH_HOLD_MINUTES=60` and nothing else), `act_refuse` 4/4
(file unchanged). The checker flagged documents in four act briefs: three where the main session
added its own document for the file it read (`source.path` outside the schema), one where
documents reached the brief without `cost_tokens` after the worker's check. Four OpenCode runs in
the final batch hung at start-up while other OpenCode sessions were starting on the same
machine; they were stopped and rerun one at a time, 20 seconds apart.
