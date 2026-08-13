---
paths:
  - "src/api/**/*.js"
---

# API conventions

- Every route handler takes `(req, callback)` and calls back exactly once.
- New endpoints are added to the `routes` array, never registered elsewhere.
- A route that reads users must filter `deleted_at`.
