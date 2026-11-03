# Chapter 4: Fixing Unreliable Tool Routing

| Path | What it is |
|---|---|
| `skills/` | The four skills the chapter builds: `code-review` and `explain-module` (knowledge), `fix-lint` and `migrate-module` (action) |
| `descriptions/` | The four `code-review` descriptions the routing test compares: A vague, B specific, C over-specific, D (B without the redirect clauses) |
| `eval/prompts.jsonl` | Twenty prompts, ten unambiguous and ten ambiguous, each with the skill it should reach and why |
| `eval/run-routing.sh` | Runs every prompt in a fresh session on a fresh copy of `sample-project/`, in Claude Code or OpenCode, and records the first skill loaded (`none` if none) |
| `eval/score.py` | Scores a results file, split into the two halves |
| `runs/2026-10-27-routing/` | 320 real sessions: four descriptions, two runs each, in Claude Code and OpenCode |
| `runs/2026-10-27-access/` | Tests of user-only and model-only skills, tool rules, and `context: fork` in Claude Code, and two runs of the earlier `migrate-module`, which had no file list |
| `runs/2026-11-03-action-skill/` | The current `migrate-module`, twice in Claude Code and twice in OpenCode |
| `runs/2026-11-03-boundary/` | Four more runs of the five action/knowledge boundary prompts under versions B and D, in both harnesses |

To install the skills in a project, copy `skills/*` into `.claude/skills/` (Claude Code, also read by
OpenCode) or `.agents/skills/` (OpenAI Codex, Google Antigravity, OpenCode, Pi).

To reproduce a routing run (set `PROMPT_IDS`, for example `"11 13 15 16 17"`, to run only some prompts):

```bash
bash eval/run-routing.sh claude b results-claude-b.txt
python3 eval/score.py results-claude-b.txt
```

`run-routing.sh` runs Claude Code with `--setting-sources project,local`, so your user-level skills
don't compete with the four project skills, and gives OpenCode an `opencode.json` that
allows only those four. Sessions are headless with the harness's default permissions, so actions
that need approval are refused; the routing decision comes before that.
