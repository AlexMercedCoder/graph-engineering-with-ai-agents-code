---
name: code-review
description: Reviews a changed file or diff and reports bugs, missing error handling, and convention violations as a written list. Use when the user asks for a review, asks whether a change is safe to merge, or asks what is wrong with a file. Does not modify files. Use fix-lint for automatic style corrections.
---

# Code review

Review the file or diff the user named. Work through these checks in order.

1. Read the file and the tests that cover it.
2. Check error handling on every path that can fail. Flag any callback or promise without an error path.
3. Check the change against the conventions in the project configuration file.
4. Report findings as a list, most severe first. State the file and line for each one.

Report findings only. Do not edit files.
