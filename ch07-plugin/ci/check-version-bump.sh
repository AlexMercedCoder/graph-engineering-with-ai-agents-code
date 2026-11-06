#!/usr/bin/env bash
set -euo pipefail
base=$1 plugin=$2
manifest="$plugin/.claude-plugin/plugin.json"
git diff --quiet "$base" -- "$plugin" && { echo "ok   no changes in $plugin"; exit 0; }
old=$(git show "$base:$manifest" 2>/dev/null | jq -r .version) || old=none
new=$(jq -r .version "$manifest")
if [ "$old" = "$new" ]; then
  echo "FAIL $plugin changed since $base but version is still $new"; exit 1
fi
echo "ok   $plugin version $old -> $new"
