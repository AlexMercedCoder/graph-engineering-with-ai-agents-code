# AGS walkthroughs in MagAgent, Loro, and MagGraph (2026-11-05)

Versions: MagAgent 1.4.0 (`mag-agent[mcp]`, with LiteLLM 1.108.0), Loro 0.22.0, MagGraph 0.4.1
(CLI built from the `v0.4.1` tag, Python wheel from PyPI, `fastmcp` 4.1.6), agentic-graph-spec
1.0.4. Claude Code 2.1.316 with `claude-opus-5-5`; OpenCode 1.19.5 with `openai/gpt-6.1-sol`.
MagAgent and Loro used their offline `mock` providers, so no model was called in those runs.
Each harness ran in a fresh copy of `sample-project/` with `HOME` and the XDG directories pointed
at a throwaway folder. Local paths are replaced with `<run-dir>`.

## MagAgent (`magagent/`)

The graph is `ags/migrate-order-service.agraph.yaml`. The scripted mock sessions are in
`inputs/`: `mock-claims-done.json` records the baseline and then claims the migration without
editing a file; `mock-replay.json` writes the three files exactly as the Claude Code session in
`ch05-subagents/runs/2026-10-27-graph/graph-3.diff` left them. Setup: `magent user create reader`,
`magent provider set mock`, the Chapter 4 `migrate-module` skill copied to
`~/.config/magent/skills/`, and `magent mode silent` (`inputs/magagent-user-profile.toml`).

| Files | Mock session | Permission mode | Result |
|---|---|---|---|
| `claims-done-1`, `-2` | Claims done, no edits | silent | `migrate_module` failed both attempts on `no_db_import` (evidence `1:import { query } from '../db.js';`); `verify` skipped; run failed |
| `replay-1`, `-2` | Replays the Chapter 5 edits | silent | All nodes succeeded; 3 files changed, 17 insertions, 24 deletions |
| `replay-balanced-mode` | Replays the Chapter 5 edits | balanced (default) | `grep` criterion passed; both `node` criteria recorded as failed with no evidence (policy needs confirmation, none possible with `--yes`); run failed |
| `resume-after-edit.txt` | Resume of `claims-done-1` after changing `max_agent_steps` | silent | `RT053: graph digest changed since the saved run` |

Earlier attempts in the same session, not kept: with the core install the mock failed every call
(`No module named 'mcp'`, LiteLLM 1.108.0); with the skill only in the project's `.magent/skills/`
the run stopped with `RT012: required skills are unavailable: migrate-module`;
`allowed_shell_patterns = ["node *", "npm *"]` in `config.toml` (`inputs/magagent-config.toml`)
did not change the balanced-mode result, because the criterion runner does not read the list.

## Loro (`loro/`)

`config.local.toml` is the project configuration after `loro configure --provider mock`, plus
`[agraph] allow_command_criteria = true` and `shell`/`edit` set to `allow`.

| Files | What ran | Result |
|---|---|---|
| `validate-default-policy.json` | `loro graph validate --strict` with the default policy | `LP006` on `migrate_module` and `verify` |
| `validate-command-criteria-allowed.json`, `plan.txt` | Same after enabling command criteria | Valid, same digest as MagAgent; worst case 4 executions |
| `run-mock-1.json`, `-2.json` | `loro graph run --yes` | `run_tests` failed with `output_missing: node contract failed` (the mock can't call tools); run failed |
| `gate-without-role.json` | `gate-only.agraph.yaml`, `--yes`, no roles | Gate `blocked`, no diagnostic |
| `gate-with-maintainer-role.json` | Same with `LORO_IDENTITY_ROLES=maintainer` | Gate approved; human event recorded |
| `gate-yes-denied.txt` | Same with `[approvals] allow_non_interactive = false` | `--yes is denied by approvals.allow_non_interactive` |

Without `--yes` and without a terminal, the digest approval prompt was refused and no run started.
Before `shell`/`edit` were set to `allow`, the run failed with `RT021: permission 'fs:read:**' is
not granted`.

## MagGraph (`maggraph/`)

A four-node graph (`knowledge_graph/`, `maggraph.toml`), the scaffolded server from
`maggraph scaffold --mcp --skill`, with `SKILL.md` moved out of the graph root (left there, it
stops the index from opening: `missing field id`). `mcp.json` and `opencode.json` connect the
server with the three write tools removed.

| Files | Prompt | Result |
|---|---|---|
| `claude-code-maggraph-1`, `-2` | Services within two hops of `order-service` | One `traverse_graph` call; `payments-service` (1 hop), `audit-service` (2 hops), with paths; $0.34 and $0.14 |
| `opencode-maggraph-two-hop-1`, `-2` | Same | Same answer, one `traverse_graph` call |
| `claude-code-maggraph-delete-1`, `-2` | Delete `orders-db` | Refused; no write tool offered; graph unchanged |
| `opencode-maggraph-delete-1`, `-2` | Same | Refused; one run suggested `rm` for the user; graph unchanged |

The Claude Code and OpenCode files keep only messages, tool calls, and results.
