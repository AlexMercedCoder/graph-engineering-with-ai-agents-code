---
name: test-setup
description: How to run the orders-api test suite and what it needs; read before running tests in this project
metadata:
  type: reference
---

- The only test entry point is `npm test`, which runs `node --test` (package.json). No Makefile, pyproject, jest, or mocha config exists. Requires Node >= 20. No install step needed (no dependencies).
- `node --test` auto-discovers files under `tests/`; output is TAP-style with a summary at the end (tests/suites/pass/fail counts).
- Running `npm test` exits 1 when any test fails. Piping through `2>&1` gives the full failure detail including stack traces.
- The DB is an in-memory module (src/db.js) with setImmediate callbacks, so the suite runs in about 100 ms. No setup or teardown is needed.
