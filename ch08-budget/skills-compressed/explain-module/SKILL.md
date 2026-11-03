---
name: explain-module
description: Explains what a module does, what it depends on, and which endpoints reach it. For "how does X work", "what is X for", "what calls X". Read-only.
---

# Explain a module

1. Read the named file and anything it imports.
2. Search `src/api/routes.js` for endpoints that reach it.
3. Explain in prose: responsibility, dependencies, callers, and anything surprising.

Do not edit files. Do not suggest a refactor unless asked.
