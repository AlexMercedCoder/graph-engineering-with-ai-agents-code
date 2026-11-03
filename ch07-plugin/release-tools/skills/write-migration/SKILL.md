---
name: write-migration
description: Writes a SQL migration file for a schema change the user describes, such as adding a column or an index. Use when the user asks for a migration. Writes a draft for a person to review and move into migrations/. Does not run the migration.
---

# Write a migration

1. Read `src/db.js` to see the tables and columns.
2. Write the SQL for the change the user asked for, with a matching rollback statement in a comment.
3. Save it as `migration-drafts/<NNNN>_<short_name>.sql`, numbering from 0001. Don't write
   under `migrations/`: that folder is protected, and a person moves reviewed drafts into it.
4. Report the file name and the SQL, and say that it needs review before it moves to
   `migrations/`. Do not run it.
