# Subagent memory: `test-runner` with `memory: project`, run twice

`test-runner.md` here is the chapter's definition with `memory: project` added and one
instruction: `Before you return, add to your memory anything about this project's test setup
that would save a future run time, and nothing else.` Both runs used the failing-tests project
from `../2026-10-27-isolation/` and the same prompt, in the same project copy, one after the
other.

| Run | Subagent requests | Subagent input | What it did |
|---|---|---|---|
| `run1` | 7 | 94,697 | Listed the project, read `package.json`, ran the suite twice, read seven files, wrote two memory files |
| `run2` | 2 | 18,845 | Listed the project and ran the suite twice, with the memory index already in its prompt; wrote nothing new |

`agent-memory/` is what run 1 wrote to `.claude/agent-memory/test-runner/`: `MEMORY.md` (the
index Claude Code loads into the subagent's prompt) and `test_setup.md`. One run each, so treat
the difference as an example, not a measurement.
