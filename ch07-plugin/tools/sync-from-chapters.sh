#!/usr/bin/env bash
# Rebuild team-workflow's components from the chapter folders they come from:
# the Chapter 4 skills, the Chapter 5 agents, and the Chapter 6 hook scripts and
# settings. The hooks block of ch06-hooks/settings.json becomes hooks/hooks.json,
# with each project path rewritten to the plugin root.
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
code=$(cd "$here/.." && pwd)
p="$here/team-workflow"
rm -rf "$p/skills" "$p/agents" "$p/hooks/scripts"
mkdir -p "$p/skills" "$p/agents" "$p/hooks/scripts"
cp -r "$code"/ch04-routing/skills/* "$p/skills/"
cp "$code"/ch05-subagents/agents/*.md "$p/agents/"
cp "$code"/ch06-hooks/scripts/*.sh "$p/hooks/scripts/"
chmod +x "$p"/hooks/scripts/*.sh
python3 - "$code/ch06-hooks/settings.json" "$p/hooks/hooks.json" <<'PY'
import json, sys
hooks = json.load(open(sys.argv[1]))["hooks"]
text = json.dumps({"hooks": hooks}, indent=2)
text = text.replace("${CLAUDE_PROJECT_DIR}/.claude/hooks/", '\\"${CLAUDE_PLUGIN_ROOT}\\"/hooks/scripts/')
open(sys.argv[2], "w").write(text + "\n")
PY
echo "team-workflow rebuilt from ch04-routing, ch05-subagents, and ch06-hooks"
