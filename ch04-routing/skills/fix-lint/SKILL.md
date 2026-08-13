---
name: fix-lint
description: Applies the project formatter to named files and writes the corrected result to disk. Use when the user asks to fix, format, or clean up style problems. Modifies files. Use code-review to report problems without changing them.
---

# Fix formatting

1. Run `npm run format` for the whole project, or `node scripts/lint.js --fix <path>` for one file.
2. Report which files changed.

Do not make behavioural changes. Formatting only.
