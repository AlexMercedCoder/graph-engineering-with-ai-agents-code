---
name: code-review
description: Reports bugs, missing error handling, and convention violations in a file or diff. For reviews, "safe to merge?", "what's wrong with X". Read-only; fix-lint fixes style.
---

# Code review

Review the file or diff the user named. Work through these checks in order.

1. Read the file and the tests that cover it.
2. Check error handling on every path that can fail. Flag any callback or promise without an error path.
3. Check the change against the conventions in the project configuration file.
4. Report findings as a list, most severe first. State the file and line for each one.

Report findings only. Do not edit files.
