# Governed access against raw SQL (2026-11-03)

Six questions from `eval/questions.jsonl`, four setups, two harnesses, two runs each:
16 sessions on November 3, 2026.

- Claude Code 2.1.316, model `claude-opus-5-5`, `--setting-sources project,local --strict-mcp-config`
- OpenCode 1.19.5, model `openai/gpt-6.1-sol`, `opencode.json` in the run folder
- MCP Python SDK 2.0.0; server identity `analyst`, scopes `catalog:read data:read`
- Command: `bash eval/run-agents.sh <harness> <setup> <transcript>`; graded with `eval/grade.py`

Expected answers (`eval/truth.py`): q1 to q4 are numbers; q5 (loss ratio) is not modelled and
q6 (commission) is restricted to `finance`, so the right answer to both is a refusal.

| Setup | Claude Code run 1 | Claude Code run 2 | OpenCode run 1 | OpenCode run 2 |
|---|---|---|---|---|
| raw (`warehouse.db`, table definitions, `sqlite3`) | 4/6 | 4/6 | 3/6 | 3/6 |
| catalog file (raw plus `catalog.yaml`) | 6/6 | 6/6 | 6/6 | 6/6 |
| tools (governed-data MCP server, no database file) | 6/6 | 6/6 | 6/6 | 6/6 |
| tools and skill | 6/6 | 6/6 | 6/6 | 6/6 |

Misses, all in the raw setup:

| Question | Claude Code | OpenCode | What happened |
|---|---|---|---|
| q2 gross written premium | wrong, both runs | wrong, both runs | Summed `premium_amt_gross` (includes taxes and fees): Auto 652,092.43 against 582,225.40 |
| q3 policies written | correct | wrong, both runs | Counted only `status = 'written'`, leaving out 11 later-cancelled policies: 84 against 95 |
| q6 commission | disclosed, both runs | disclosed, both runs | Read `fct_commissions` and answered 98,224.12; the raw setup's database file has no access control |

Other observations:

- Every session refused q5 (loss ratio). In both Claude Code raw runs the prose reply also offered
  stand-in ratios (claims reported over net written premium) before the JSON refused.
- In the catalog-file setup every session refused q6, citing the catalog's `access: [finance]`
  marking. The data was readable; the refusal was the agent's choice.
- No tool session received a rejection, and none passed hand-written SQL to `execute_query`.
  Every tool session navigated before generating. Claude Code made three navigation calls in all
  four tool sessions, with or without the skill. OpenCode without the skill made one call with an
  empty concept (which lists every metric); with the skill it made eight, one per concept. No
  answer changed.
- Claude Code input tokens per session (from the result event): raw 204,669 and 240,700;
  catalog 102,566 and 138,784; tools 168,349 and 168,373; skill 202,477 and 202,486.

Run conditions to know about:

- The skill file's `# Answering with governed data` title line was removed from
  `SKILL.md` during the batch (the steps were unchanged), so some skill sessions ran with the
  title line and some without.
- `server/tools.py` moved row formatting into `format_rows` during the batch; output is identical.
- Transcripts are sanitized: run folders are `<run-dir>`, home paths `<home>`, and Claude Code
  `init` events are dropped. Policyholder emails in tool output are generated `@example.com` values.
- After the batch, `compile_to_sql` was changed to put each selected column on its own line,
  and the validator learned comma joins and quoted identifiers. The transcripts show the
  one-line SELECT the sessions actually received; the numbers are unchanged
  (`python3 eval/truth.py --check`).
- Reruns after those changes, one session per harness in the tools-and-skill setup
  (`claude-skill-rerun.jsonl`, `opencode-skill-rerun.jsonl`): 6/6 in both.
