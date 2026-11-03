#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "guard-bash: jq is not installed, so this call can't be checked. Install jq." >&2; exit 2; }

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""') || { echo "guard-bash: couldn't read the hook input, so the call is refused." >&2; exit 2; }

deny() {
  echo "Blocked: $1" >&2
  echo "$2" >&2
  exit 2
}

shopt -s nocasematch
if   [[ "$cmd" =~ rm[[:space:]]+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|-r[[:space:]]+-f|-f[[:space:]]+-r|--recursive) ]]; then deny "recursive delete" "Delete specific files by name, or ask the user."
elif [[ "$cmd" =~ git[[:space:]]+push ]];                       then deny "push to remote" "Commit locally and let the user push."
elif [[ "$cmd" =~ git[[:space:]]+reset[[:space:]]+--hard ]];    then deny "hard reset" "Use git stash to set changes aside instead."
elif [[ "$cmd" =~ chmod[[:space:]]+(-R[[:space:]]+)?0?777 ]];   then deny "world-writable permissions" "Grant the narrowest mode the task needs."
elif [[ "$cmd" =~ (curl|wget).*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z)?sh ]]; then deny "piping a download to a shell" "Download, inspect, then run explicitly."
fi

exit 0
