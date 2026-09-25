# Chapter 1: Escaping the Prompt Loop

The setup and the three exercises from Chapter 1, each run against
`sample-project/`.

## Setup

```bash
git clone https://github.com/AlexMercedCoder/graph-engineering-with-ai-agents-code
cd graph-engineering-with-ai-agents-code
./verify.sh
```

`verify.sh` runs everything checkable without an agent, a network connection,
or an API key. It should report `passed 18, failed 0`.

## Exercise 1: instruction decay

Work on a throwaway branch (`git switch -c ch01-experiments`), then start a
session in `sample-project/` and send the rule first:

```text
Project rule: all database access goes through the repository classes in
src/repositories/. Code in src/services/ must never import query() or
update() from src/db.js. Use UserRepository and OrderRepository for all
data operations.
```

Then the task:

```text
Move src/services/user-service.js and src/services/order-service.js onto
UserRepository and OrderRepository. Keep soft-delete working. Then change
totalPaidCents so the paid-total report leaves out orders from deleted
users, and update the tests to match. Run npm test when you're done.
```

Fixing the report breaks the existing test that expects 14,600 cents (it
counts a $5 order from Alan, a soft-deleted user). Check the rule afterward:

```bash
grep -n "db.js" src/services/user-service.js src/services/order-service.js
```

Any output is a violation. The chapter shows the kind of edit to look for:
it fetches orders through `OrderRepository`, falls back to `query()` for the
users, and passes all ten tests while breaking the rule.

## Exercise 2: tool-selection drift

In a fresh session in `sample-project/`, ask:

```text
In src/services/user-service.js, what does findUser return when no user
has the given id?
```

The direct route is one or two tool calls: read that file, and perhaps
`tests/user-service.test.js`. The answer is `null`.

## Exercise 3: cost explosion

Run a short task (`write a unit test for findUser`) and a multi-file task
(`move order-service.js onto OrderRepository, update its callers, and fix the
tests`) in separate fresh sessions, and record request counts plus input,
cached, and output tokens from your harness's usage display.
