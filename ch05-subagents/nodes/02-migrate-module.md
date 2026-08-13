node: migrate-module
brief: Migrate the single service module named in MODULE from callback-style
       database access to the matching repository class. Convert its exported
       functions to return promises and update its test file to await them.
       Change no other file.
inputs: MODULE (a path under src/services/), docs in ch04-routing/skills/migrate-module/SKILL.md
outputs: modified src/services/<module>.js and tests/<module>.test.js
success: node --test tests/<module>.test.js exits zero
