#!/usr/bin/env bash
# Install governed-change from the marketplace into a throwaway configuration
# and a fresh project, then compare what loaded with what the plugin ships.
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
plugin=$here/marketplace/plugins/governed-change
export CLAUDE_CONFIG_DIR=$(mktemp -d)
project=$(mktemp -d)
trap 'cd /; rm -rf "$CLAUDE_CONFIG_DIR" "$project"' EXIT

cd "$project"
claude plugin marketplace add "$here/marketplace" --scope project > /dev/null
claude plugin install governed-change@platform-workflows --scope project > /dev/null
details=$(claude plugin details governed-change@platform-workflows)

want_skills=$(find "$plugin" -name SKILL.md | wc -l | tr -d ' ')
want_hooks=$(jq '.hooks | keys | length' "$plugin/hooks/hooks.json")
want_mcp=$(jq '.mcpServers | keys | length' "$plugin/.mcp.json")
count() { sed -n "s/^ *$1 (\([0-9]*\)).*/\1/p" <<< "$details" | grep . || echo 0; }
status=0
for kind in "Skills:$want_skills" "Hooks:$want_hooks" "MCP servers:$want_mcp"; do
  name=${kind%%:*}; want=${kind#*:}; got=$(count "$name")
  if [ "$got" != "$want" ]; then echo "FAIL $name: loaded $got, plugin ships $want"; status=1
  else echo "ok   $name: $got"; fi
done
exit $status
