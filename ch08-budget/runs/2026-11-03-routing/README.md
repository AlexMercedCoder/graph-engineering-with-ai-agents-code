# Routing: specific, compressed, and grouped skills

Chapter 4's twenty prompts (`../../../ch04-routing/eval/prompts.jsonl`), each in a fresh session on a
fresh copy of `sample-project/`, run with `../../eval/run-variant.sh` twice per version per harness:

```bash
bash eval/run-variant.sh claude ../ch04-routing/skills results-flat.txt
bash eval/run-variant.sh claude skills-compressed results-compressed.txt
bash eval/run-variant.sh claude skills-grouped results-grouped.txt
python3 ../ch04-routing/eval/score.py results-grouped.txt
```

The route recorded is the procedure file the agent read from `.claude/skill-groups/` (grouped version),
otherwise the first skill loaded through the skill tool, otherwise `none`.

| Version | Claude Code run 1 | Claude Code run 2 | OpenCode run 1 | OpenCode run 2 |
|---|---|---|---|---|
| Specific (`ch04-routing/skills`) | 15 | 16 | 20 | 20 |
| Compressed (`skills-compressed/`) | 17 | 16 | 20 | 19 |
| Grouped (`skills-grouped/`) | 20 | 20 | 20 | 20 |

Every miss was a session that loaded no skill: in Claude Code, prompts 12, 13, 15, 18, and 20 for the
specific version and 13, 15, 18, and 20 for the compressed one; in OpenCode, prompt 20 once for the
compressed version. In every grouped session the agent loaded the expected category and then read the
expected procedure file. Grouped Claude Code sessions took a median of 7 requests against 6 for the
other versions, the extra one being the read of the procedure file. Their first request was slightly
larger (median 31,368 against 31,124) because, with no project `code-review` skill, Claude Code's
built-in `code-review` skill appears in the listing.

Files: `<harness>/results-<version>-run<n>.txt` and `<harness>/transcripts/<version>-<prompt>-<run>.jsonl`.
Local paths are replaced with `<run-dir>`.
