---
paths:
  - "src/repositories/**/*.js"
---

# Repository conventions

- One class per table. Methods return promises, never take callbacks.
- Query construction happens here and nowhere else.
- A new repository follows the shape of `UserRepository`.
