# Skills against inline guidance, on the book's own manuscript configuration

The manuscript repository for this book keeps a 3,195-byte `CLAUDE.md` and about 124,000 bytes of
writing and figure guidance in two skills, `book` and `images`. We copied that configuration (the
`CLAUDE.md` and the skills' Markdown files) into an empty Git repository, and made a second copy with
every skill file appended to `CLAUDE.md` and no skills. One prompt that needs no files, twice each, in
Claude Code 2.1.316 with `claude-opus-5-5`, `--setting-sources project,local`, November 5, 2026:

| Configuration | Run 1 | Run 2 |
|---|---|---|
| Guidance in skills (`skills-*.jsonl`) | 33,196 | 33,193 |
| Guidance inline in `CLAUDE.md` (`inline-*.jsonl`) | 75,272 | 75,273 |

First-request payloads, from `../../../ch03-context-wall/measure-usage.py --csv`.
