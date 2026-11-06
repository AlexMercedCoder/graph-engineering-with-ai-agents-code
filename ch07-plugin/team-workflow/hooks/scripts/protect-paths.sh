#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "protect-paths: jq is not installed, so this call can't be checked. Install jq." >&2; exit 2; }

input=$(cat)
fields=$(printf '%s' "$input" | jq -r '[.tool_name // "", .tool_input.file_path // "", .cwd // ""] | @tsv') || { echo "protect-paths: couldn't read the hook input, so the call is refused." >&2; exit 2; }
IFS=$'\t' read -r tool path cwd <<<"$fields"

case "$tool" in
  Write|Edit) ;;
  *) exit 0 ;;
esac

root=${CLAUDE_PROJECT_DIR:-$cwd}
path=${path#"$root"/}

guarded=""
case "/$path" in
  */migrations/*) guarded="migrations/" ;;
  */terraform/*)  guarded="terraform/" ;;
esac
case "${path##*/}" in
  .env|.env.*)       guarded=".env" ;;
  package-lock.json) guarded="package-lock.json" ;;
esac

if [[ -n "$guarded" ]]; then
  echo "Blocked write to $path. Paths matching $guarded require human review." >&2
  echo "Describe the change you need and ask the user to make it." >&2
  exit 2
fi

exit 0
