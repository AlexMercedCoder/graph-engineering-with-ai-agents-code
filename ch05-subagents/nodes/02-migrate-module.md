node: migrate-module
brief: Migrate the single service module named in MODULE from callback-style
       database access to the matching repository class. Convert its exported
       functions to return promises and update its test file to await them.
       Update the callers in src/api/routes.js so every route still responds.
       Change no other file.
inputs: MODULE (a path under src/services/), and the migrate-module skill from Chapter 4
        (.claude/skills/migrate-module/SKILL.md once installed)
outputs: modified src/services/<module>.js, tests/<module>.test.js, and src/api/routes.js
success: node --test tests/<module>.test.js and node scripts/check-routes.js both exit zero
