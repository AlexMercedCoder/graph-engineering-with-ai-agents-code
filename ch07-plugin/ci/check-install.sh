#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
plugin="$here/team-workflow"
export CLAUDE_CONFIG_DIR=$(mktemp -d)
project=$(mktemp -d)
trap 'rm -rf "$CLAUDE_CONFIG_DIR" "$project"' EXIT

cd "$project"
claude plugin validate --strict "$plugin" >/dev/null
claude plugin marketplace add "$here" --scope project >/dev/null
claude plugin install team-workflow@book-platform --scope project >/dev/null
details=$(claude plugin details team-workflow@book-platform)

want_skills=$(find "$plugin" -name SKILL.md | wc -l | tr -d ' ')
want_agents=$(find "$plugin" -path '*/agents/*.md' | wc -l | tr -d ' ')
want_hooks=$(jq '.hooks | keys | length' "$plugin/hooks/hooks.json")

count() { sed -n "s/^ *$1 (\([0-9]*\)).*/\1/p" <<<"$details" | grep . || echo 0; }
status=0
for kind in Skills:$want_skills Agents:$want_agents Hooks:$want_hooks; do
  name=${kind%%:*}; want=${kind#*:}; got=$(count "$name")
  if [ "$got" != "$want" ]; then
    echo "FAIL $name: loaded $got, plugin ships $want"; status=1
  else
    echo "ok   $name: $got"
  fi
done
exit $status
