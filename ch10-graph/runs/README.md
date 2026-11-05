# Chapter 10 runs, 2026-11-03

| Folder | What it holds |
|---|---|
| `2026-11-03-extraction/` | Two extraction runs with four relationship types and two with five, `claude-sonnet-5-5` through Claude Code 2.1.316 |
| `2026-11-03-retrieval/` | `recall.py -v` output for the vector baseline |
| `2026-11-03-benchmark/` | 160 agent sessions answering the twenty questions (`final/`), plus earlier passes kept for reference |
| `2026-11-03-ladybug/` | The graph loaded into LadybugDB and queried in Cypher |
| `2026-11-03-refresh/` | A model-backed incremental refresh after editing one document and deleting another |

Transcripts have the `init` and rate-limit events removed and local paths replaced.
