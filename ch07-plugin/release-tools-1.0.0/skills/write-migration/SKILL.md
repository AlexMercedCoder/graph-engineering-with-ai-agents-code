---
name: write-migration
description: Writes a SQL migration file for a schema change the user describes, such as adding a column or an index. Use when the user asks for a migration. Does not run the migration.
---

# Write a migration

1. Read `src/db.js` to see the tables and columns.
2. Write the SQL for the change the user asked for, with a matching rollback statement in a comment.
3. Save it as `migrations/<NNNN>_<short_name>.sql`, numbering from 0001.
4. Report the file name and the SQL. Do not run it.
