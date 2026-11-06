# The budget check

`check-budget.py --ceiling 33000 --save <file> <project>` on fresh copies of `sample-project/`, in
Claude Code 2.1.316 with `claude-opus-5-5`, November 5, 2026, twice per configuration:

| Configuration | Run 1 | Run 2 | Result |
|---|---|---|---|
| Split (`CLAUDE.core.md` as `CLAUDE.md`, plus `rules/` in `.claude/rules/`) | 31,877 | 31,874 | ok |
| 146-line guide (`CLAUDE.monolithic.md` as `CLAUDE.md`) | 33,585 | 33,584 | FAIL, 585 over |

`verify.sh` replays `split-1.jsonl` and `monolithic-1.jsonl` with `--log`, so the check's logic is
tested without a model call.
