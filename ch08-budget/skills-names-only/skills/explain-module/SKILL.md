---
name: explain-module
description: Explains what one module does, what it depends on, and which endpoints reach it, as prose. Use when the user asks how something works, what a module is for, or what calls it. Reads only; does not modify files.
---

# Explain a module

1. Read the named file and anything it imports.
2. Search `src/api/routes.js` for endpoints that reach it.
3. Explain in prose: responsibility, dependencies, callers, and anything surprising.

Do not edit files. Do not suggest a refactor unless asked.
