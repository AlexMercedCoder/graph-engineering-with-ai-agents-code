# Chapter 8: Balancing the Context Budget

| Path | What it is |
|---|---|
| `CLAUDE.monolithic.md` | The 146-line project guide the chapter prunes: a directory tree, a dependency section, an architecture overview, concept explanations, formatter-default conventions, and the rules that matter |
| `CLAUDE.pruned.md` | The same guide cut to the lines that change the agent's output (39 lines) |
| `CLAUDE.core.md` and `rules/` | The split configuration: a 23-line core for `CLAUDE.md`, and three path-scoped rules for `.claude/rules/` (`api-conventions.md`, `repository-conventions.md`, `test-conventions.md`) |
| `loaded-context.py` | Lists what Claude Code loaded into a session, request by request: instruction files, path-scoped rules, skill listing changes, compaction boundaries, and each request's payload |
| `skills-compressed/` | Chapter 4's four skills with compressed descriptions (210 listing tokens against 340) |
| `skills-grouped/` | The same four skills as two category skills (`inspect-code`, `change-code`) in `skills/`, with the procedures in `skill-groups/` |
| `eval/run-variant.sh` | Runs Chapter 4's twenty routing prompts against a skill set and records the procedure each session reached |
| `runs/` | Real runs from 2026-11-03; see `runs/README.md` |

## Reading your own bill

```bash
claude -p "<a task you run every week>" --output-format stream-json --verbose > task.jsonl
python3 ../ch03-context-wall/measure-usage.py --each task.jsonl
python3 loaded-context.py --latest <project-dir>
```

`loaded-context.py` reads Claude Code's session file for the project
(`~/.claude/projects/<project-folder>/<session-id>.jsonl`) and prints nothing from it but the
loading events and payloads. Output for a session that read the router with the split configuration:

```text
  load    skill listing: 17 skills, 7989 chars
  load    instructions: CLAUDE.md (717 chars)
request   1  payload   31,862  then Read
  load    path-scoped: .claude/rules/api-conventions.md (224 chars)
request   2  payload   32,666
```

## Installing the split configuration

```bash
cp CLAUDE.core.md <project>/CLAUDE.md
mkdir -p <project>/.claude/rules && cp rules/*.md <project>/.claude/rules/
```

For a harness without path-scoped rules, keep the core in the always-loaded file, put the three
rules (without their frontmatter) in `docs/rules/api.md`, `repositories.md`, and `tests.md`, and
add this line to the core:

```text
Before reading or editing files under `src/api/`, `src/repositories/`, or `tests/`, read the matching file in `docs/rules/`: `api.md`, `repositories.md`, or `tests.md`.
```

## Running the routing comparison

```bash
bash eval/run-variant.sh claude ../ch04-routing/skills results-flat.txt
bash eval/run-variant.sh claude skills-compressed results-compressed.txt
bash eval/run-variant.sh opencode skills-grouped results-grouped.txt
python3 ../ch04-routing/eval/score.py results-grouped.txt
```

Set `OPENCODE_MODEL` to pick OpenCode's model and `PROMPT_IDS` to run only some prompts. The
script runs Claude Code headless with `--setting-sources project,local`, and gives OpenCode an
`opencode.json` that allows only the variant's skills. In our runs (two per version per harness),
the specific, compressed, and grouped versions scored 31, 33, and 40 of 40 in Claude Code 2.1.316
and 40, 39, and 40 in OpenCode 1.19.5.
