---
paths:
  - "tests/**/*.test.js"
---

# Test conventions

- `node:test` and `node:assert/strict` only. No test framework dependency.
- A callback-style export is tested with the `(t, done)` signature.
- A promise-returning export is tested with an async function.
