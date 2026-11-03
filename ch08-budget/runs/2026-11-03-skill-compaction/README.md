# An invoked skill's body across /compact

A `release-checklist` skill with `FIRST RULE (marker TOPMARK-7731)` on its first line and
`LAST RULE (marker ENDMARK-4419)` on its last. Step 1 loads it, step 2 runs `/compact`, step 3 asks
the agent, without reading anything, to quote both lines.

| Runs | Skill size | Loaded by | Body attached again after compaction | Answer |
|---|---|---|---|---|
| `1`, `2` | about 9,000 tokens (180 table rows) | `/release-checklist` slash command | No, both | Could give the lines only as the summary paraphrased them |
| `tool-1`, `tool-2` | about 9,000 tokens | Skill tool (`Use the release-checklist skill ...`) | No, both | Same |
| `small-1`, `small-2` | about 1,700 tokens (30 rows) | Skill tool | No, both; the payload after compaction grew only by the summary | Same |

The documentation says invoked skills are re-attached after compaction, up to 5,000 tokens per
skill. These were headless sessions compacted with `/compact`.

In one continuous process (`../2026-11-03-single-process/`), the skill did come back after `/compact`, truncated to its first 20,000 characters, as the documentation describes. The difference is the resume boundary between separate processes.
