---
name: code-review
description: Reviews a release before it ships, checking that CHANGELOG.md, the version in package.json, and the migration files agree. Use when the user asks to review a release or whether a version is ready to tag. Does not modify files.
---

# Release review

1. Read CHANGELOG.md and package.json.
2. List the files under migrations/.
3. Report any version or changelog entry that disagrees with the others, as a list. Do not edit files.
