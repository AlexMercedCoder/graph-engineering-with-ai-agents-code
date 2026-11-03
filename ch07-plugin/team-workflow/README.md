# team-workflow

The Part 2 execution graph from *Graph Engineering with AI Agents*, packaged: four skills
(`code-review`, `explain-module`, `fix-lint`, `migrate-module`), three agents (`test-runner`,
`module-migrator`, `migration-dispatcher`), and six hooks (`protect-paths`, `guard-bash`,
`confirm-destructive-sql`, `lint-on-edit`, `test-on-stop`, `audit`).

    /plugin install team-workflow@book-platform     # from the book-platform marketplace
    claude --plugin-dir ./team-workflow             # try it without installing
    claude plugin details team-workflow             # check what loaded

Components sit at the plugin root; only `plugin.json` goes in `.claude-plugin/`. Hook commands use
`"${CLAUDE_PLUGIN_ROOT}"`, because an installed plugin's root is a cache folder named after its
version. The hooks assume the book's sample project: `lint-on-edit.sh` runs `node scripts/lint.js`
and `test-on-stop.sh` runs `npm test`.

Don't edit this folder by hand. Change the chapter folders it comes from and run
`../tools/sync-from-chapters.sh`.
