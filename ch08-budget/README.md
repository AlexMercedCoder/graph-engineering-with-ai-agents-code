# Chapter 8: Balancing the Context Budget

| Path | What it is |
|---|---|
| `CLAUDE.monolithic.md` | The 146-line project guide the chapter prunes: a directory tree, a dependency section, an architecture overview, concept explanations, formatter-default conventions, and the rules that matter |
| `CLAUDE.pruned.md` | The same guide cut to the lines that change the agent's output (39 lines) |
| `CLAUDE.core.md` and `rules/` | The split configuration: a 23-line core for `CLAUDE.md`, and three path-scoped rules for `.claude/rules/` (`api-conventions.md`, `repository-conventions.md`, `test-conventions.md`) |
| `loaded-context.py` | Lists what Claude Code loaded into a session, request by request: instruction files, path-scoped rules, skill listing changes, compaction boundaries, and each request's payload |
| `check-budget.py` | Starts a fresh headless Claude Code session in a project and fails (exit 1) when the first request's payload is over the ceiling you give it; `--log` checks a recorded session instead |
| `skills-compressed/` | Chapter 4's four skills with compressed descriptions (210 listing tokens against 340) |
| `skills-grouped/` | The same four skills as two category skills (`inspect-code`, `change-code`) in `skills/`, with the procedures in `skill-groups/` |
| `skills-names-only/` | Chapter 4's four skills unchanged, with a `settings.json` whose `skillOverrides` lists each by name only |
| `eval/run-variant.sh` | Runs Chapter 4's twenty routing prompts against a skill set and records the procedure each session reached |
| `runs/` | Real runs from 2026-11-03 and 2026-11-05; see `runs/README.md` |

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

## Holding the fixed part to a ceiling

```bash
python3 check-budget.py --ceiling 33000 <project-dir>
```

The check sends one prompt that needs no tools, with `--setting-sources project,local`, and compares
the first request's payload (harness baseline, configuration, skill listing, MCP tool names) with the
ceiling. On `sample-project/`, the split configuration passed at 31,877 tokens and the 146-line guide
failed at 33,585. Run it as a CI step on every change to the configuration, skills, or MCP settings;
it costs one request of about 32,000 tokens. The ceiling includes the harness, so a Claude Code
upgrade can fail it too: measure again and change the ceiling in a commit that says why.

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

With `skills-names-only/`, the four skills listed by name only routed 5 and 7 of 20 on November 5,
2026, against 14 and 15 for the full descriptions the same day; every miss loaded no skill.
