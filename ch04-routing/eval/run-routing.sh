#!/usr/bin/env bash
# Run the Chapter 4 routing evaluation: every prompt in prompts.jsonl, each in a fresh
# session and a fresh copy of the project, and record which skill the harness chose.
#
#   bash eval/run-routing.sh claude b results-claude-b.txt
#   bash eval/run-routing.sh opencode b results-opencode-b.txt
#   python3 eval/score.py results-claude-b.txt
#
# The second argument picks the code-review description from descriptions/: a (vague),
# b (specific), c (over-specific), or d (b without the redirect clauses, which also removes
# the matching clause from fix-lint). Needs the harness signed in, Python 3, and Git.
#
# Set OPENCODE_MODEL (for example openai/gpt-6.1-sol) to pick OpenCode's model.
# Claude Code runs with --setting-sources project,local so your user-level skills
# don't compete with the four project skills. OpenCode gets an opencode.json that allows
# only the four project skills. Runs are headless with the harness's default permissions,
# so actions that need approval are refused; the routing decision happens before that.
set -euo pipefail
harness=${1:?usage: run-routing.sh claude|opencode a|b|c|d <results-file>}
version=${2:?usage: run-routing.sh claude|opencode a|b|c|d <results-file>}
out=${3:?usage: run-routing.sh claude|opencode a|b|c|d <results-file>}
here=$(cd "$(dirname "$0")/.." && pwd)
project="$here/../sample-project"
work=$(mktemp -d)
logs="${LOGS:-$work/logs}"; mkdir -p "$logs"
desc=$(cat "$here"/descriptions/version-"$version"-*.yaml)
: > "$out"

python3 - "$here/eval/prompts.jsonl" > "$work/prompts.tsv" <<'PY'
import json, sys
for line in open(sys.argv[1]):
    if line.strip():
        r = json.loads(line)
        print(f"{r['id']}\t{r['prompt']}")
PY

while IFS=$'\t' read -r id prompt; do
  d="$work/run-$id"
  cp -r "$project" "$d"; rm -rf "$d/.agent-work"
  mkdir -p "$d/.claude/skills"; cp -r "$here"/skills/* "$d/.claude/skills/"
  python3 - "$d/.claude/skills/code-review/SKILL.md" "$desc" <<'PY'
import re, sys
p, d = sys.argv[1], sys.argv[2].strip()
s = open(p).read()
open(p, "w").write(re.sub(r"^description: .*$", lambda m: d, s, count=1, flags=re.M))
PY
  if [ "$version" = d ]; then   # version D also drops fix-lint's redirect clause
    sed -i 's/ Modifies files. Use code-review to report problems without changing them.//' "$d/.claude/skills/fix-lint/SKILL.md"
  fi
  (cd "$d" && git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.com commit -qm baseline)
  log="$logs/$version-$id.jsonl"
  case "$harness" in
    claude)
      (cd "$d" && claude -p "$prompt" --setting-sources project,local --max-turns 8 \
        --output-format stream-json --verbose < /dev/null > "$log" 2>/dev/null) || true ;;
    opencode)
      cat > "$d/opencode.json" <<'JSON'
{"$schema": "https://opencode.ai/config.json",
 "permission": {"skill": {"*": "deny", "code-review": "allow", "explain-module": "allow",
                          "fix-lint": "allow", "migrate-module": "allow"}}}
JSON
      (cd "$d" && opencode run --format json ${OPENCODE_MODEL:+-m "$OPENCODE_MODEL"} "$prompt" < /dev/null > "$log" 2>/dev/null) || true ;;
    *) echo "unknown harness: $harness" >&2; exit 1 ;;
  esac
  chosen=$(python3 - "$log" <<'PY'
import json, sys
for line in open(sys.argv[1], errors="replace"):
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        continue
    if e.get("type") == "assistant":                      # Claude Code stream-json
        for c in e["message"].get("content", []):
            if c.get("type") == "tool_use" and c.get("name") == "Skill":
                print(c["input"].get("skill")); sys.exit()
    part = e.get("part") or {}                            # OpenCode --format json
    if part.get("tool") == "skill":
        print((part.get("state") or {}).get("input", {}).get("name")); sys.exit()
print("none")
PY
)
  echo "$id $chosen" | tee -a "$out"
done < "$work/prompts.tsv"
echo "transcripts: $logs"
