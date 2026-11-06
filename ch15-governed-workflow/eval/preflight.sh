#!/usr/bin/env bash
# The deployment checklist, as checks that run without a model.
#
#   bash eval/preflight.sh [saved-run ...]
#
# Each line checks one connection between components built in different
# chapters. Pass saved Claude Code run folders to check their traces too.
# Uses ports 8817 and 8818; stop anything else on them first.
set -uo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
root=$here/..
plugin=$here/marketplace/plugins/governed-change
pass=0; fail=0
check() {
  local name=$1; shift
  if "$@" > /dev/null 2>&1; then echo "  ok    $name"; pass=$((pass + 1))
  else echo "  FAIL  $name"; fail=$((fail + 1)); fi
}

echo "packaging"
check "plugin validates (--strict)"           claude plugin validate --strict "$plugin"
check "marketplace validates (--strict)"      claude plugin validate --strict "$here/marketplace"
check "plugin installs with every component"  bash "$here/eval/check-install.sh"
check "act-on-evidence matches Chapter 12"   diff -r "$root/ch12-router/skills/act-on-evidence" "$plugin/skills/act-on-evidence"
check "retrieve-evidence matches Chapter 12" diff -r "$root/ch12-router/skills/retrieve-evidence" "$plugin/skills/retrieve-evidence"
check "audit hook matches Chapter 6"          diff "$root/ch06-hooks/scripts/audit.sh" "$plugin/hooks/scripts/audit.sh"
check "workflow graph validates (AGS --strict)" ags-validate --strict --quiet "$here/graph/change-config.agraph.yaml"

echo "knowledge side"
check "router routes 36/42 by rules"          bash -c "cd '$root/ch12-router/eval' && python3 check_router.py"
check "every path returns an evidence envelope" bash -c "cd '$root/ch12-router/eval' && python3 check_server.py"
check "graph matches the deployment manifest" python3 "$root/ch10-graph/eval/check_manifest.py"

echo "execution and governance"
check "gate guarantees hold"                  python3 "$here/eval/check_gate.py"
check "Chapter 6 guards and redaction hold"   bash "$root/ch06-hooks/tests/check-guards.sh"

echo "servers"
python3 -c "import json,sys,time; t=json.load(open(sys.argv[1])); sys.exit(min(v['exp'] for v in t.values()) < time.time() + 600)" \
  "$here/config/test-tokens.json" 2> /dev/null || python3 "$here/tools/make-test-tokens.py" > /dev/null
set -a; . "$here/config/test-tokens.env"; set +a
state=$(mktemp -d)
py=$(python3 -c 'import sys; print(sys.executable)')     # the interpreter itself, so $! is its PID
(cd "$here/servers" && GOVERNED_STATE=$state exec "$py" knowledge_http.py > /dev/null 2>&1) & k=$!
(cd "$here/servers" && GOVERNED_STATE=$state exec "$py" gate_server.py > /dev/null 2>&1) & g=$!
sleep 5
status() { curl -s -o /dev/null -w '%{http_code}' -X POST "$1" -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' "${@:2}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'; }
check "knowledge server refuses a missing token" test "$(status http://127.0.0.1:8817/mcp)" = 401
check "gate refuses the knowledge token"      test "$(status http://127.0.0.1:8818/mcp -H "Authorization: Bearer $GOVERNED_KNOWLEDGE_TOKEN")" = 401
check "gate accepts its own token"            test "$(status http://127.0.0.1:8818/mcp -H "Authorization: Bearer $GOVERNED_GATE_TOKEN")" != 401
kill "$k" "$g" 2> /dev/null; wait "$k" "$g" 2> /dev/null; rm -rf "${state:?}"

if [ $# -gt 0 ]; then
  echo "traces"
  for run in "$@"; do check "trace complete: $(basename "$run")" python3 "$here/eval/check_trace.py" "$run"; done
fi

echo
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
