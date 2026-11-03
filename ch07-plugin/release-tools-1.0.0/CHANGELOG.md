# Changelog

## 1.1.0
`write-migration` writes drafts to `migration-drafts/` and says a person moves reviewed drafts into
`migrations/`, which team-workflow's `protect-paths.sh` protects.

## 1.0.0
`write-migration` wrote straight into `migrations/` and was refused by team-workflow's hook. Kept in
`../release-tools-1.0.0/` to reproduce the collision.
