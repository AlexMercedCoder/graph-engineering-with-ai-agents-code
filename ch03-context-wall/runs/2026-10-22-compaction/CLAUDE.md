# Project rules

- 1. All database access goes through the repository classes in src/repositories/. Code in src/services/ must not import query() or update() from src/db.js in anything you add or change.
- 2. Every new or changed function gets a test.
- 3. No new dependencies: package.json keeps an empty dependency list.
