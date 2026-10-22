# Chapter 3 rule scope: task 7 rerun with a reworded rule 1, 2026-10-22

Both fresh Claude Code ladder runs (`../2026-10-22-ladder/cc-fresh-*`) scored 2 of 3 on task 7:
they changed the import line in `src/services/user-service.js` but kept `update` from `../db.js`
for `softDeleteUser`, a function the task didn't touch. These two runs start from each fresh
run's own task 6 commit and rerun task 7 in a fresh session, with rule 1 reworded
(`reworded-rules.txt`):

> If you edit a file in src/services/, that whole file must end up with no import of query() or
> update() from src/db.js, including for functions your task doesn't otherwise touch.

| Run | Starts from | Task 7 score | `db.js` imports left in `user-service.js` |
|---|---|---|---|
| `cc-reword-1` | `cc-fresh-1` task 6 | `task7 aas=3/3 c1=1 c2=1 c3=1` | none |
| `cc-reword-2` | `cc-fresh-2` task 6 | `task7 aas=3/3 c1=1 c2=1 c3=1` | none |

Claude Code 2.1.308, `claude-opus-5-5`, same flags as the ladder. `changes.diff` holds the
whole history of each working copy; the last commit, `task7`, is the rerun.
