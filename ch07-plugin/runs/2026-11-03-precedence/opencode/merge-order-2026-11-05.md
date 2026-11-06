# Reproducing the reordered merge (2026-11-05)

OpenCode 1.19.5, `opencode debug config`, no model, with `XDG_CONFIG_HOME`, `XDG_DATA_HOME`,
`XDG_CACHE_HOME`, and `XDG_STATE_HOME` pointed at an empty scratch folder.

Project `opencode.json`: `{"permission":{"bash":{"*":"allow","node scripts/check-routes.js*":"deny"}}}`

| `OPENCODE_CONFIG` file (loads before the project) | Merged `permission` |
|---|---|
| `{"permission":{"bash":{"node scripts/check-routes.js*":"allow"}}}` | `{"bash":{"node scripts/check-routes.js*":"deny","*":"allow"}}` |
| `{"permission":{"bash":{"git status":"allow"}}}` | `{"bash":{"git status":"allow","*":"allow","node scripts/check-routes.js*":"deny"}}` |

When both files set the same key, the project's value wins but the key stays where the earlier file
put it. In the first case that moves the deny ahead of `"*": "allow"`, and the last-match rule then
lets every command through. Keys only the project sets follow in the project's order.

Status as of 2026-11-05: last-match-wins is documented (opencode.ai/docs/permissions) and was
confirmed as intended for v1 and v2 by a maintainer closing issue #37935 in
github.com/anomalyco/opencode (October 22, 2026). We found no issue about merge position. OpenCode
2.x (v2.2.5, October 30, 2026) was not tested here.
