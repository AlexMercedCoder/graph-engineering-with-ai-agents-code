#!/usr/bin/env bash
# Runs every case in commands.txt and paths.txt through the shell hooks and the OpenCode plugin,
# and every line of secrets.txt through audit.sh.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0; n=0
project=/work/terraform/app

expect_code() { [[ $1 == block || $1 == overblock ]] && echo 2 || echo 0; }

while read -r expect cmd; do
  [[ -z "$expect" || "$expect" == \#* ]] && continue
  n=$((n+1))
  jq -n --arg c "$cmd" '{tool_name:"Bash",tool_input:{command:$c}}' | scripts/guard-bash.sh 2>/dev/null; got=$?
  [[ $got == $(expect_code "$expect") ]] || { echo "FAIL guard-bash ($expect, exit $got): $cmd"; fail=1; }
done < tests/commands.txt

while read -r expect path; do
  [[ -z "$expect" || "$expect" == \#* ]] && continue
  n=$((n+1))
  path=${path//<project>/$project}
  jq -n --arg p "$path" --arg d "$project" '{tool_name:"Write",cwd:$d,tool_input:{file_path:$p}}' \
    | CLAUDE_PROJECT_DIR= scripts/protect-paths.sh 2>/dev/null; got=$?
  [[ $got == $(expect_code "$expect") ]] || { echo "FAIL protect-paths ($expect, exit $got): $path"; fail=1; }
done < tests/paths.txt

work=$(mktemp -d)
while read -r expect secret cmd; do
  [[ -z "$expect" || "$expect" == \#* ]] && continue
  n=$((n+1))
  (cd "$work" && jq -n --arg c "$cmd" '{session_id:"t",hook_event_name:"PreToolUse",tool_name:"Bash",tool_input:{command:$c}}' | "$OLDPWD/scripts/audit.sh")
  if grep -qF -- "$secret" "$work/.agent-work/audit.jsonl"; then kept=1; else kept=0; fi
  [[ $expect == mask && $kept == 1 ]] && { echo "FAIL audit kept a secret: $cmd"; fail=1; }
  [[ $expect == gap && $kept == 0 ]] && { echo "FAIL audit now masks a listed gap (reclassify it): $cmd"; fail=1; }
done < tests/secrets.txt
rm -rf "$work"

node tests/check-plugin.mjs || fail=1

(( fail )) && exit 1
echo "guards: $n shell cases and the plugin match tests/commands.txt, tests/paths.txt, and tests/secrets.txt"
