# Project configuration (core)

## Project context

A small order-management API in plain JavaScript, ESM, no dependencies. Tests run
with the built-in Node test runner.

## Architecture rules

- Database access goes through the repository classes in `src/repositories/`.
- Services in `src/services/` are mid-migration off callback-style access.
- No new dependencies. `package.json` keeps an empty dependency list.

## Workflow rules

- After changing anything in `src/`, run `npm test`.
- Do not modify `migrations/`, `.env`, or any lock file.

## Scope

Work on the feature described in the current task. Do not refactor unrelated code.

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
