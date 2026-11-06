# Routing with skills listed by name only

Chapter 4's twenty prompts (`../../../ch04-routing/eval/prompts.jsonl`), each in a fresh session on a
fresh copy of `sample-project/`, in Claude Code 2.1.316 with `claude-opus-5-5`, run twice per version
with `../../eval/run-variant.sh` on November 5, 2026:

```bash
bash eval/run-variant.sh claude skills-names-only results-names-only.txt
bash eval/run-variant.sh claude ../ch04-routing/skills results-specific.txt
python3 ../ch04-routing/eval/score.py results-names-only.txt
```

`skills-names-only/` is Chapter 4's four skills, unchanged, plus a `settings.json` whose
`skillOverrides` sets each to `"name-only"`, so the listing shows `- code-review` and nothing else.
The specific version is the same-day control.

| Version | Run 1 | Run 2 | Median first request |
|---|---|---|---|
| Specific (full descriptions) | 14 | 15 | 31,144 |
| Names only | 5 | 7 | 30,860 |

Every miss in all four runs was a session that loaded no skill. With names only, the agent still
loaded `code-review` for prompts 1 and 2, `migrate-module` for 5 and 6, and `explain-module` for 7,
where the prompt nearly repeats the name, and in run 2 also `fix-lint` for 11 and `migrate-module`
for 14. The unambiguous half routed 5 of 10 in both runs and the ambiguous half 0 and 2.

OpenCode has no name-only listing state, so these runs are Claude Code only.

Files: `results-<version>-run<n>.txt` and `transcripts/<version>-<prompt>-<run>.jsonl`. Local paths
are replaced with `<run-dir>` and `<home>`, and the local user name with `user`.
