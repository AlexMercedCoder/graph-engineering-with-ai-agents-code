# The Chapter 3 task ladder

Seven tasks of increasing scope against `sample-project/`. Run the ladder twice:
once with a fresh session per task, once as one continuous session. The gap
between the two accuracy curves at the same task number is the cost of the
shared context window.

## Declare these three constraints in turn 1 of every run

1. All database access goes through the repository classes in `src/repositories/`.
2. Every new or changed function has a test.
3. No new dependencies. `package.json` keeps an empty dependency list.

Score AAS out of 3 after each task by checking the diff against them.

## The tasks

| # | Task | Touches |
|---|---|---|
| 1 | Add a `findByEmail` method to `UserRepository` and a test for it | 2 files |
| 2 | Make `listActiveUsers` in `user-service.js` use `UserRepository` | 2 files |
| 3 | Add an `OrderRepository.findQuotes()` method and a test | 2 files |
| 4 | Migrate all of `order-service.js` to `OrderRepository`, updating its tests | 2 files, whole module |
| 5 | Add a `PaymentRepository`, migrate `payment-service.js`, update its tests | 3 files |
| 6 | Add a `GET /users/:id/payments` endpoint with a test, using the repositories | 3 files + router |
| 7 | Add soft-delete filtering to every read path, add a report endpoint, run the suite | 4+ files, router, tests |

Task 1 is small enough to stay in the effective zone. Task 7 will not, which is
the point.

## Recording the numbers

    node --test 2>&1 | tee /tmp/task-3.log
    python3 parse-usage.py /tmp/task-3.log --task 3 --tokens 24000 --aas 3 >> curve.csv

Then plot `curve.csv` with any spreadsheet: TPR on the horizontal axis, AAS on
the vertical.
