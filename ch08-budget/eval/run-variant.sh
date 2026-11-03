#!/usr/bin/env bash
# Run Chapter 4's twenty routing prompts against a variant skill set, each in a fresh
# session on a fresh copy of sample-project/, and record which procedure the agent reached.
#
#   bash eval/run-variant.sh claude skills-compressed results-claude-compressed.txt
#   bash eval/run-variant.sh opencode skills-grouped results-opencode-grouped.txt
#   python3 ../ch04-routing/eval/score.py results-claude-compressed.txt
#
# A variant directory holds skills/ (installed into .claude/skills/) and, for a grouped
# variant, skill-groups/ (installed into .claude/skill-groups/, where the harness doesn't
# discover them). A flat variant may hold the skill folders directly. The route recorded is
# the member procedure the agent read from .claude/skill-groups/, if any, otherwise the first
# skill it loaded through the skill tool, otherwise none. Set OPENCODE_MODEL to pick
# OpenCode's model and PROMPT_IDS to run only some prompts.
set -euo pipefail
harness=${1:?usage: run-variant.sh claude|opencode <variant-dir> <results-file>}
variant=$(cd "${2:?variant dir}" && pwd)
out=${3:?results file}
here=$(cd "$(dirname "$0")/.." && pwd)
project="$here/../sample-project"
prompts="$here/../ch04-routing/eval/prompts.jsonl"
work=$(mktemp -d)
logs="${LOGS:-$work/logs}"; mkdir -p "$logs"
: > "$out"
python3 - "$prompts" > "$work/prompts.tsv" <<'PY'
import json, os, sys
ids = os.environ.get("PROMPT_IDS", "").split()
for line in open(sys.argv[1]):
    if line.strip():
        r = json.loads(line)
        if not ids or str(r["id"]) in ids:
            print(f"{r['id']}\t{r['prompt']}")
PY
while IFS=$'\t' read -r id prompt; do
  d="$work/run-$id"
  cp -r "$project" "$d"; rm -rf "$d/.agent-work"; mkdir -p "$d/.claude/skills"
  if [ -d "$variant/skills" ]; then cp -r "$variant"/skills/* "$d/.claude/skills/"; else cp -r "$variant"/* "$d/.claude/skills/"; fi
  [ -d "$variant/skill-groups" ] && cp -r "$variant/skill-groups" "$d/.claude/skill-groups"
  (cd "$d" && git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.com commit -qm baseline)
  log="$logs/$id.jsonl"
  case "$harness" in
    claude)
      (cd "$d" && claude -p "$prompt" --setting-sources project,local --max-turns 8 \
        --output-format stream-json --verbose < /dev/null > "$log" 2>/dev/null) || true ;;
    opencode)
      names=$(ls "$d/.claude/skills" | python3 -c 'import json,sys; print(json.dumps({n.strip(): "allow" for n in sys.stdin if n.strip()}))')
      echo "{\"\$schema\": \"https://opencode.ai/config.json\", \"permission\": {\"skill\": $(python3 -c "import json; d={'*':'deny'}; d.update($names); print(json.dumps(d))")}}" > "$d/opencode.json"
      (cd "$d" && opencode run --format json ${OPENCODE_MODEL:+-m "$OPENCODE_MODEL"} "$prompt" < /dev/null > "$log" 2>/dev/null) || true ;;
    *) echo "unknown harness: $harness" >&2; exit 1 ;;
  esac
  chosen=$(python3 - "$log" <<'PY'
import json, re, sys
first_skill, member = None, None
pat = re.compile(r"skill-groups/[\w-]+/([\w-]+)\.md")
for line in open(sys.argv[1], errors="replace"):
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        continue
    calls = []
    if e.get("type") == "assistant":
        calls = [(c.get("name"), c.get("input", {})) for c in e["message"].get("content", []) if c.get("type") == "tool_use"]
    part = e.get("part") or {}
    if part.get("tool"):
        calls = [(part["tool"], (part.get("state") or {}).get("input", {}))]
    for name, inp in calls:
        if name in ("Skill", "skill") and first_skill is None:
            first_skill = inp.get("skill") or inp.get("name")
        m = pat.search(json.dumps(inp))
        if m and member is None:
            member = m.group(1)
print(member or first_skill or "none")
PY
)
  echo "$id $chosen" | tee -a "$out"
done < "$work/prompts.tsv"
echo "transcripts: $logs"
