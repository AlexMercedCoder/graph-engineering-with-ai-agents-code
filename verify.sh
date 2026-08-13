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

echo "chapter 4, routing evaluation"
check "scorer runs and reports the split" python3 ch04-routing/eval/score.py ch04-routing/eval/results.example.txt

echo "chapter 6, hooks"
check "protect-paths blocks migrations/" bash -c 'echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"migrations/1.sql\"}}" | ch06-hooks/scripts/protect-paths.sh; [ $? -eq 2 ]'
check "protect-paths allows src/"        bash -c 'echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/a.js\"}}" | ch06-hooks/scripts/protect-paths.sh'
check "guard-bash blocks rm -rf"         bash -c 'echo "{\"tool_input\":{\"command\":\"rm -rf /\"}}" | ch06-hooks/scripts/guard-bash.sh; [ $? -eq 2 ]'

echo "chapter 9, knowledge server"
check "error code lookup"        bash -c "cd ch09-mcp/server && python3 cli.py error-code E4021 | grep -q 'authorization expired'"
check "unknown code suggests neighbours" bash -c "cd ch09-mcp/server && python3 cli.py error-code E4023 | grep -q E4022"
check "schema hides secret values" bash -c "cd ch09-mcp/server && python3 cli.py config-schema payments | grep -q 'value not shown'"
check "data scoping hides restricted section" bash -c "cd ch09-mcp/server && KB_IDENTITY=engineer python3 cli.py architecture 'fraud scoring' | grep -q 'No architecture sections'"

echo "chapter 10, knowledge graph"
check "extraction builds the graph" bash -c "cd ch10-graph/graph && python3 extract.py | grep -q 'nodes'"
check "multi-hop traversal finds RenewalsWorker" bash -c "cd ch10-graph/graph && python3 query.py dependents NotificationsAPI 3 | grep -q RenewalsWorker"
check "config blast radius"         bash -c "cd ch10-graph/graph && python3 query.py config PAYMENT_API_KEY | grep -q PaymentsService"
check "benchmark harness runs"      bash -c "cd ch10-graph/eval && python3 run_graph_side.py | grep -q '10/10'"

echo "chapter 11, semantic layer"
if python3 -c "import yaml" 2>/dev/null; then
  check "valid request compiles to SQL" bash -c "cd ch11-catalog && python3 validate.py --metric net_written_premium --dimensions region | grep -q 'JOIN analytics.dim_geography'"
  check "invalid dimension is refused"  bash -c "cd ch11-catalog && ! python3 validate.py --metric net_written_premium --dimensions claim_severity"
  check "invented table is caught"      bash -c "cd ch11-catalog && python3 validate.py --sql 'SELECT 1 FROM analytics.fct_premiums' 2>&1 | grep -q 'Nearest match'"
else
  echo "  skip  chapter 11 needs PyYAML (pip install pyyaml)"
fi

echo "chapter 12, retrieval router"
check "router scores 12/12 on its eval set" bash -c "python3 ch12-router/router.py --eval ch12-router/queries.jsonl | grep -q '12/12'"

echo
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
