# Chapter 3: Surviving the Context Wall

| File | What it does |
|---|---|
| `task-ladder.md` | The three rules, the seven tasks, the compaction test, and the stress test, with the commands to run after each task |
| `measure-usage.py` | Reads Claude Code's `--output-format stream-json` output or an OpenAI Codex session log and prints the payload of every request |
| `score-task.sh` | Scores one task's changes against the three rules (AAS out of 3) and commits them |
| `record-curve.py` | Appends one row per task to a CSV file (`--csv`, default `curve.csv`) |
| `make-logs.py` | Writes the seven synthetic log files the stress test reads, from a fixed seed |
| `runs/2026-10-22-ladder/` | Eight ladder runs: Claude Code and OpenAI Codex, one continuous session and fresh sessions, twice each, plus the compaction test |
| `runs/2026-10-22-compaction/` | The compaction tests: no-rules controls, the `recordLogin` probe with the rules in a message, in `CLAUDE.md`, or in a file the agent read, and fresh controls |
| `runs/2026-10-22-rule-scope/` | Task 7 rerun in fresh sessions with rule 1 reworded to state its scope |
| `runs/2026-10-22-stress/` | The stress test: a search-based version and a file-reading-tool version, twice each per harness |

Everything here uses the Python standard library. Run it from a working copy of `sample-project/` that is its own Git repository; `task-ladder.md` shows how to set one up.
