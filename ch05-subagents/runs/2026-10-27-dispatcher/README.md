# Dispatcher: four modules, one session versus one worker per module

Prompt for `single-*` (with `--disallowedTools Agent`): migrate every module in `src/services/` one
at a time, running each module's tests. Prompt for `dispatch-*`: `Use the migration-dispatcher
subagent to migrate every module in src/services/ to the repository pattern.` All runs:
`claude -p ... --permission-mode acceptEdits --allowedTools "Bash(node --test*)" "Bash(npm
test*)" "Bash(mkdir *)" "Bash(ls *)"`. `summary.txt` has the outcome of each run: test results
afterward, services still importing `db.js`, and files changed.

The agent definitions changed between runs (`agents-*/`). "Routes" is `node scripts/check-routes.js`
afterward, which no test covers.

| Runs | Definitions | Safeguard errors | Modules migrated | Routes |
|---|---|---|---|---|
| `single-1`, `-2` | (no subagents) | none | all four, both | 5 of 5 respond, both |
| `dispatch-1` to `-4` | `notes-sonnet`: worker step 5 says `Write your full working notes to ...` | in 1, 2, 3 | 1: two lost; 2: all four after retries; 3: one lost; 4: all four | 1: 2 broken; 2: 5 broken; 3: 4 broken; 4: 5 broken |
| `dispatch-5`, `-6` | `notes-inherit`: same, worker on the main model | in both | 5: none (all four workers stopped); 6: all four after retries | 5: all respond (nothing changed); 6: 5 broken |
| `dispatch-7`, `-8` | `record-sonnet`: step 5 asks for `a short record ...: what changed, which tests you ran and their result, and anything you skipped and why.` | none | 7: partial (the dispatcher narrowed the workers' jobs); 8: all four | 7: 2 broken; 8: 5 broken |
| `dispatch-9`, `-10` | `record-scope`: the dispatcher is told not to add limits to a worker's job | none | all four, both | 5 broken, both |
| `dispatch-11`, `-12` | `record-scope-callers`: the dispatcher's last step starts one general-purpose agent to run the route check and update `src/api/routes.js` | none | all four, both | 5 of 5 respond, both |

`../../agents/migration-dispatcher.md` is `agents-record-scope-callers/` with one sentence of step 5
reworded after the runs ("Workers each own one module, so none of them will change the callers"),
because the transcripts show workers did read `routes.js` and reported the breakage as out of scope.

The safeguard errors were API responses such as `Sonnet 5.5's safeguards flagged this message`, with
`[reasoning_extraction]` in the details. `dispatch-1`, `-2`, and `-6` retried the failed workers
once; the retries rescued `-2` and `-6`. Every module worker sees one service, so no worker updated
the router that calls them; the single sessions and the agent team (`../2026-10-27-team/`) did.

Token figures, from each session's own transcript (`workers/<run>/` holds the subagent transcripts,
user and assistant messages only; `dispatch-2` and `-6` include retried workers):

| Run | Main session peak, total input | Subagent sessions (dispatcher and workers) | Their peaks | Their total input | All input |
|---|---|---|---|---|---|
| `single-1` | 32,330, 302,690 | (none) | | | 302,690 |
| `single-2` | 31,742, 241,637 | (none) | | | 241,637 |
| `dispatch-2` | 22,486, 85,069 | 6 | 7,226 to 11,589 | 212,158 | 297,227 |
| `dispatch-4` | 26,071, 89,701 | 5 | 8,828 to 11,596 | 226,309 | 316,010 |
| `dispatch-6` | 23,938, 87,812 | 9 (four stopped at once) | up to 13,191 | 255,560 | 343,372 |
| `dispatch-8` | 22,559, 84,912 | 5 | 7,756 to 9,713 | 174,566 | 259,478 |
| `dispatch-9` | 21,711, 62,743 | 5 | 8,789 to 9,706 | 179,742 | 242,485 |
| `dispatch-10` | 22,927, 86,467 | 5 | 9,103 to 10,281 | 236,722 | 323,189 |
| `dispatch-11` | 25,467, 113,764 | 6 (with the callers agent) | 8,777 to 20,379 | 315,541 | 429,305 |
| `dispatch-12` | 22,722, 86,652 | 6 (with the callers agent) | 8,681 to 18,578 | 336,365 | 423,017 |

Each worker's hand-back to the dispatcher was about 790 to 1,450 characters: about 480 characters
of header that Claude Code adds to every subagent result, the four-line report (about 200
characters, most of it the file's absolute path), and an agent ID and usage footer.

`routes/` holds the output of `node scripts/check-routes.js` in each copy afterward. A trailing `timeout: the monitored command dumped core` line is Node crashing on exit on the author's machine, after the check printed its result.
