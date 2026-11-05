#!/usr/bin/env bash
# Runs everything in this repository that can be checked without a harness,
# a network, or a paid API key. If this passes on your machine, every exercise
# that does not need an agent will work.
set -uo pipefail
cd "$(dirname "$0")"
pass=0; fail=0
check() {
  local name="$1"; shift
  if "$@" >/tmp/verify-out 2>&1; then
    echo "  ok    $name"; pass=$((pass+1))
  else
    echo "  FAIL  $name"; sed 's/^/          /' /tmp/verify-out | tail -5; fail=$((fail+1))
  fi
}

echo "sample project"
check "npm test (10 tests, zero dependencies)" bash -c "cd sample-project && npm test"
check "formatter reports clean"                bash -c "cd sample-project && node scripts/lint.js"
check "every API route answers"                bash -c "cd sample-project && node scripts/check-routes.js"

echo "chapter 4, routing evaluation"
check "scorer runs and reports the split" python3 ch04-routing/eval/score.py ch04-routing/runs/2026-10-27-routing/claude-code/results-b-run1.txt
check "execution graph dry-runs" bash ch05-subagents/run-graph.sh src/services/order-service.js

echo "chapter 6, hooks"
check "protect-paths blocks migrations/" bash -c 'echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"migrations/1.sql\"}}" | ch06-hooks/scripts/protect-paths.sh; [ $? -eq 2 ]'
check "protect-paths allows src/"        bash -c 'echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/a.js\"}}" | ch06-hooks/scripts/protect-paths.sh'
check "guard-bash blocks rm -rf"         bash -c 'echo "{\"tool_input\":{\"command\":\"rm -rf /\"}}" | ch06-hooks/scripts/guard-bash.sh; [ $? -eq 2 ]'
check "confirm-destructive-sql asks"     bash -c 'echo "{\"tool_input\":{\"command\":\"DELETE FROM users\"}}" | ch06-hooks/scripts/confirm-destructive-sql.sh | grep -q "\"ask\""'
check "lint-on-edit flags a db.js import" bash -c 'cd sample-project && echo "{\"tool_input\":{\"file_path\":\"$PWD/src/services/auth-service.js\"}}" | ../ch06-hooks/scripts/lint-on-edit.sh >/dev/null 2>&1; [ $? -eq 2 ]'
check "audit writes a trace line"        bash -c 'd=$(mktemp -d); s=$PWD/ch06-hooks/scripts/audit.sh; cd "$d" && echo "{\"tool_name\":\"Read\",\"hook_event_name\":\"PreToolUse\",\"session_id\":\"s\",\"tool_input\":{\"file_path\":\"a\"}}" | "$s" && grep -q PreToolUse .agent-work/audit.jsonl; r=$?; rm -rf "$d"; exit $r'

echo "chapter 7, plugin"
check "plugin scripts match chapter 6"   diff -r ch06-hooks/scripts ch07-plugin/team-workflow/hooks/scripts
check "plugin hooks use the plugin root" bash -c "python3 -c 'import json; json.load(open(\"ch07-plugin/team-workflow/hooks/hooks.json\"))' && ! grep -q CLAUDE_PROJECT_DIR ch07-plugin/team-workflow/hooks/hooks.json"

echo "chapter 8, context budget"
check "loaded-context script parses" python3 -m py_compile ch08-budget/loaded-context.py
check "variant router parses"        bash -n ch08-budget/eval/run-variant.sh

echo "chapter 9, knowledge server"
check "error code lookup"        bash -c "cd ch09-mcp/server && python3 cli.py error-code E4021 | grep -q 'authorization expired'"
check "unknown code suggests neighbours" bash -c "cd ch09-mcp/server && python3 cli.py error-code E4023 | grep -q E4022"
check "schema hides secret values" bash -c "cd ch09-mcp/server && python3 cli.py config-schema payments | grep -q 'value not shown'"
check "data scoping hides restricted section" bash -c "cd ch09-mcp/server && KB_IDENTITY=engineer python3 cli.py architecture 'fraud scoring' | grep -q 'No architecture sections'"
if python3 -c "import mcp.server" 2>/dev/null; then
  check "server lists three tools" bash -c "cd ch09-mcp/server && python3 -c 'import asyncio,server;assert len(asyncio.run(server.mcp.list_tools()))==3'"
  check "HTTP gates hold" bash -c 'cd ch09-mcp && python3 tools/make-test-tokens.py >/dev/null && { python3 server/http_server.py >/dev/null 2>&1 & P=$!; sleep 3; python3 tools/check-gates.py | grep -q "all gates hold"; r=$?; kill -9 $P; exit $r; }'
else
  echo "  skip  chapter 9 server checks need the MCP SDK (pip install \"mcp>=2,<3\")"
fi

echo "chapter 10, knowledge graph"
check "extraction builds the graph" bash -c "cd ch10-graph/graph && python3 extract.py | grep -q 'nodes'"
check "multi-hop traversal finds RenewalsWorker" bash -c "cd ch10-graph/graph && python3 query.py dependents NotificationsAPI 3 | grep -q RenewalsWorker"
check "config blast radius"         bash -c "cd ch10-graph/graph && python3 query.py config PAYMENT_API_KEY | grep -q PaymentsService"
check "benchmark harness runs"      bash -c "cd ch10-graph/eval && python3 run_graph_side.py | grep -q '10/10'"
check "refresh matches a rebuild"   bash -c "cd ch10-graph/eval && python3 check_refresh.py"
check "extraction guards fire"      bash -c "cd ch10-graph/eval && python3 check_guards.py"

echo "chapter 11, semantic layer"
if python3 -c "import yaml" 2>/dev/null; then
  check "valid request compiles to SQL" bash -c "cd ch11-catalog && python3 validate.py --metric net_written_premium --dimensions region | grep -q 'JOIN analytics.dim_geography'"
  check "invalid dimension is refused"  bash -c "cd ch11-catalog && ! python3 validate.py --metric net_written_premium --dimensions claim_severity"
  check "invented table is caught"      bash -c "cd ch11-catalog && python3 validate.py --sql 'SELECT 1 FROM analytics.fct_premiums' 2>&1 | grep -q 'Nearest match'"
  check "compiled SQL matches hand-written SQL" bash -c "cd ch11-catalog && python3 warehouse/seed.py >/dev/null && python3 eval/truth.py --check"
  check "lineage check catches the gross column" bash -c "cd ch11-catalog && python3 validate.py --sql 'SELECT SUM(premium_amt_gross) AS gross_written_premium FROM analytics.fct_policy_premium' | grep -q 'not in its lineage'"
  check "comma join is caught"           bash -c "cd ch11-catalog && ! python3 validate.py --sql 'SELECT p.email FROM analytics.fct_policy_premium f, analytics.dim_policyholder p'"
  check "executor refuses hand-written SQL" bash -c "cd ch11-catalog && CATALOG_SCOPES='catalog:read data:read' python3 server/cli.py execute --sql 'SELECT 1 FROM analytics.fct_policy_premium' | grep -q 'did not come from'"
  check "row policy limits emea-analyst" bash -c "cd ch11-catalog && CATALOG_IDENTITY=emea-analyst CATALOG_SCOPES='catalog:read data:read' python3 server/cli.py ask net_written_premium region 2026-Q3 | grep -q '(1 row)'"
  check "analyst can't see commission"   bash -c "cd ch11-catalog && ! python3 server/cli.py navigate commission | grep -q commission_paid"
else
  echo "  skip  chapter 11 needs PyYAML (pip install pyyaml)"
fi

echo "chapter 12, retrieval router"
check "router scores 12/12 on its eval set" bash -c "python3 ch12-router/router.py --eval ch12-router/queries.jsonl | grep -q '12/12'"

echo
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
