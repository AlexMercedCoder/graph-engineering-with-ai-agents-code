# Project configuration (core)

The always-loaded core. Everything path-specific lives in `.claude/rules/`.

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
