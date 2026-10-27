# Chapter 4 routing runs, 2026-10-27

Twenty prompts from `../../eval/prompts.jsonl`, each in a fresh headless session on a fresh copy
of `sample-project/` (committed clean, so there is never a diff to review) with the four skills in
`.claude/skills/`. Only the `code-review` description changes between versions
(`../../descriptions/`), except that version D also removes the matching redirect clause from
`fix-lint`. Two runs per version per harness, 320 sessions.

- **Claude Code** 2.1.308, `claude-opus-5-5`: `claude -p "<prompt>" --setting-sources project,local
  --max-turns 8 --output-format stream-json --verbose`. The setting sources leave out the author's
  user-level skills; Claude Code's built-in skills stayed available (`context/` shows the listing).
- **OpenCode** 1.19.0, `openai/gpt-6.1-sol`: `opencode run --format json -m openai/gpt-6.1-sol
  "<prompt>"`, with `opencode/opencode.json` allowing only the four project skills.

A prompt counts as routed to the first skill the session loaded through the harness's skill tool
(`Skill` in Claude Code, `skill` in OpenCode), or `none`.

Correct routes, out of 20 per run. Two OpenCode sessions, `d-4-1` and `d-8-1`, first ended with no
output at all (no events, nothing on standard error), which isn't a routing decision; both were
rerun the same day, and the table and transcripts are from the reruns:

| Version | Claude Code run 1 | Claude Code run 2 | OpenCode run 1 | OpenCode run 2 |
|---|---|---|---|---|
| A, vague | 14 | 12 | 20 | 19 |
| B, specific | 17 | 17 | 20 | 20 |
| C, over-specific | 9 | 11 | 13 | 14 |
| D, B without redirect clauses | 16 | 15 | 19 | 19 |

The only wrong-skill picks were prompt 13 (`Can you look at the formatting in order-service.js?`)
under version D in OpenCode, which loaded `fix-lint` in both runs. Every other miss loaded no skill
through the skill tool. In 20 of Claude Code's 49 such sessions, the agent opened skill files with
a file read, `cat`, `head`, or `tail` instead, and each time the files it opened included the intended skill:
a-12-1, a-12-2, a-15-2, a-17-2, a-18-1, a-18-2, b-15-2, b-18-1, c-1-1, c-4-1, c-15-1, c-17-1,
c-17-2, c-18-1, c-18-2 (all four skills), d-4-2, d-15-1, d-15-2, d-18-1, d-18-2. OpenCode never did.

`context/context-version-<v>.md` is Claude Code's `/context` output for each version, run headless
in the same setup (the MCP tool list is removed): `code-review` is under 20 tokens in version A,
about 100 in B, about 130 in C, and about 80 in D, where `fix-lint` drops from about 80 to 60.

Files: `results-<version>-run<n>.txt` (the format `score.py` reads) and
`transcripts/<version>-<prompt>-<run>.jsonl`. Claude Code `init` events (which list local
configuration) and thinking-token counters are removed, and local paths are replaced with
placeholders.
