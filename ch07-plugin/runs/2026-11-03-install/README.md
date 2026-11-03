# Install, details, and versions

No model sessions; each command ran once in a throwaway `CLAUDE_CONFIG_DIR`. Paths are replaced with
`<scratch>`.

| File | What happened |
|---|---|
| `v1-local-directory.txt` | `claude plugin marketplace add <dir> --scope project` and `claude plugin install team-workflow@book-platform --scope project` wrote `extraKnownMarketplaces` and `enabledPlugins` to the project's `.claude/settings.json`. The plugin loads in place from the marketplace folder ("Read from: .../team-workflow"). `claude plugin details` listed 4 skills, 3 agents, and 3 hook events, and projected about 431 always-on tokens |
| `v2-git-1.0.0.txt` | The marketplace entry's source is `{"source": "url", "url": "file://.../tw.git"}`. Installing version 1.0.0 created `cache/book-platform/team-workflow/1.0.0/`. (`claude plugin marketplace add file://...` is rejected; a marketplace needs a path, a URL to `marketplace.json`, or a GitHub repository) |
| `v2-versions.txt` | (1) A commit to `protect-paths.sh` without a version change: `team-workflow is already at the latest version (1.0.0).`, and the cached script didn't change. (2) Version 1.1.0: `updated from 1.0.0 to 1.1.0`, a new `1.1.0/` folder, and `.orphaned_at` in `1.0.0/`. (3) No `version` field, two commits: updated to `4efe5bdbef70`, then to `6bc06e575fdb` |
| `v3-nested-skills.txt` | `skills/` moved under `.claude-plugin/`: `claude plugin validate` passed, install succeeded, `claude plugin details` showed `Skills (0)` |
