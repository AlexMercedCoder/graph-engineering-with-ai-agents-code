# orders-api: project guide for the agent

This file tells the agent everything it needs to know about the project. Read it carefully
before starting any task.

## What this project is

orders-api is a small order-management API written in plain JavaScript using ES modules.
It has users, orders, and payments, and it exposes five read-only HTTP routes. It is used
as the worked example throughout the book, so it is intentionally small and has no external
dependencies. The code is organized into layers: a database module, repositories, services,
and a router. Each layer has a single responsibility, which keeps the code easy to follow.

## Directory structure

```
orders-api/
  package.json            project manifest and npm scripts
  src/
    db.js                 in-memory database with a callback API
    api/
      routes.js           the five HTTP routes
    repositories/
      user-repository.js  UserRepository class
      order-repository.js OrderRepository class
    services/
      auth-service.js     login and active-user checks
      order-service.js    order lookups and the paid total
      payment-service.js  payment lookups and the uncaptured total
      user-service.js     user lookups and soft delete
  scripts/
    lint.js               the project formatter
    check-routes.js       calls every route and reports which respond
  tests/
    auth-service.test.js
    order-service.test.js
    payment-service.test.js
    repositories.test.js
    user-service.test.js
```

## Dependencies

The project has no runtime dependencies and no development dependencies. It uses only
Node.js built-in modules: `node:test` for tests, `node:assert/strict` for assertions, and
`node:fs` in the scripts. Node.js 20 or newer is required. There is no lock file because
there is nothing to lock.

## Architecture overview

The database module (`src/db.js`) stores three tables in memory: users, orders, and
payments. It exports `query(table, predicate, callback)` and `update(table, id, patch,
callback)`, both of which call back asynchronously using `setImmediate`. The repositories
wrap these callbacks in promises. The services call either the database directly (older
code) or the repositories (newer code). The router maps each HTTP route to a service
function and passes a callback that receives the result.

## Key concepts

### The repository pattern

The repository pattern is a design pattern in which each table, or aggregate, gets one
class that owns every query against it. The rest of the code asks the repository for data
instead of building queries itself. This keeps data access in one place, makes it easier to
change how data is stored, and makes services easier to test, because a test can replace
the repository with a fake. Repositories usually expose methods named after what the caller
needs, such as `findActive()` or `findPaid()`, rather than generic query methods.

### Callbacks and promises

A callback is a function you pass to another function so that it can call you back when
an asynchronous operation finishes. By convention in Node.js, the first argument is an
error (or null) and the second is the result. A promise is an object that represents a
value that will be available later; you can `await` it inside an `async` function. Promises
avoid deeply nested callbacks and make error handling more uniform with `try` and `catch`.
The project is moving from callbacks to promises.

### Soft deletes

A soft delete marks a row as deleted by setting a `deleted_at` timestamp instead of
removing the row. This keeps history and allows recovery, but every query that should only
see live rows has to filter on `deleted_at === null`. Forgetting that filter is the most
common soft-delete bug.

## Coding conventions

- Use ES module syntax (`import` and `export`), not CommonJS (`require`).
- Use two-space indentation.
- Use single quotes for strings.
- End statements with semicolons.
- Use `const` by default and `let` only when a variable is reassigned. Never use `var`.
- Use camelCase for variables and functions and PascalCase for classes.
- Keep functions short and focused on one job.
- Write clear, descriptive names.
- Add comments where the code is not self-explanatory.
- Handle errors on every path; never swallow an error.
- Prefer early returns over deeply nested conditionals.

## Architecture rules

- Database access goes through the repository classes in `src/repositories/`.
- Services in `src/services/` are mid-migration off callback-style access.
- No new dependencies. `package.json` keeps an empty dependency list.

## API conventions

- Every route handler takes `(req, callback)` and calls back exactly once.
- New endpoints are added to the `routes` array, never registered elsewhere.
- A route that reads users must filter `deleted_at`.

## Repository conventions

- One class per table. Methods return promises, never take callbacks.
- Query construction happens here and nowhere else.
- A new repository follows the shape of `UserRepository`.

## Test conventions

- `node:test` and `node:assert/strict` only. No test framework dependency.
- A callback-style export is tested with the `(t, done)` signature.
- A promise-returning export is tested with an async function.

## Commands

- Run all tests: `npm test`
- Run one module's tests: `node --test tests/<module>.test.js`
- Check formatting: `npm run lint`
- Fix formatting: `npm run format`
- Check that every route responds: `node scripts/check-routes.js`

## Workflow rules

- After changing anything in `src/`, run `npm test`.
- Do not modify `migrations/`, `.env`, or any lock file.
- Write a test for every new or changed function.
- Keep commits small and focused.
- Write clear commit messages in the imperative mood.

## Scope

Work on the feature described in the current task. Do not refactor unrelated code.

## Final reminders

Always read this file before starting. Always follow the conventions above. If something is
unclear, ask before guessing. Be careful, be thorough, and double-check your work.
