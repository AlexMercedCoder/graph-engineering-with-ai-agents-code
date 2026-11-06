# Pinning a Git source with ref and sha

No model sessions; each command ran once on 2026-11-05 in a throwaway `CLAUDE_CONFIG_DIR`, Claude
Code 2.1.316. The plugin is a copy of `team-workflow` 1.0.0 committed to a local bare repository and
tagged `v1.0.0` (commit A). Two marketplaces list it with a `url` source:

- pinned: `{"source": "url", "url": "file://<scratch>/tw.git", "ref": "v1.0.0", "sha": "<A>"}`
- tag only: `{"source": "url", "url": "file://<scratch>/tw.git", "ref": "v1.0.0"}`

| Step | Result |
|---|---|
| 1. Install from the pinned marketplace | `cache/book-platform/team-workflow/1.0.0/`, original `protect-paths.sh` |
| 2. Append `# TAG-MOVED` to `protect-paths.sh`, commit (B), move tag `v1.0.0` to B with `git tag -f`, force-push | |
| 3. `claude plugin marketplace update` and `claude plugin update` on the pinned install | `team-workflow is already at the latest version (1.0.0).`; script unchanged |
| 4. Fresh install from the pinned marketplace | `1.0.0/`, original script (no `TAG-MOVED`) |
| 5. Fresh install from the tag-only marketplace | `1.0.0/`, changed script (`TAG-MOVED` present) |

The version folder is `1.0.0` in steps 4 and 5, so the version doesn't reveal which commit was
installed.
