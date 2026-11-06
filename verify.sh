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
check "Chapter 6 guards match their cases" bash -c "cd ch06-hooks && tests/check-guards.sh"

echo "chapter 7, plugin"
check "plugin scripts match chapter 6"   diff -r ch06-hooks/scripts ch07-plugin/team-workflow/hooks/scripts
check "version-bump check refuses an unbumped change" bash -c 'r=$PWD; T=$(mktemp -d); cp -r ch07-plugin/team-workflow "$T/"; cd "$T" && git init -q && git add -A && git -c user.name=v -c user.email=v@example.com commit -qm v && echo "# change" >> team-workflow/hooks/scripts/protect-paths.sh && out=$("$r/ch07-plugin/ci/check-version-bump.sh" HEAD team-workflow); [[ $out == FAIL* ]]; s=$?; rm -rf "$T"; exit $s'
if command -v claude >/dev/null; then
  check "plugin installs with every component" ch07-plugin/ci/check-install.sh
fi
check "plugin hooks use the plugin root" bash -c "python3 -c 'import json; json.load(open(\"ch07-plugin/team-workflow/hooks/hooks.json\"))' && ! grep -q CLAUDE_PROJECT_DIR ch07-plugin/team-workflow/hooks/hooks.json"

echo "chapter 8, context budget"
check "loaded-context script parses" python3 -m py_compile ch08-budget/loaded-context.py
check "variant router parses"        bash -n ch08-budget/eval/run-variant.sh
check "budget script parses"                        python3 -m py_compile ch08-budget/check-budget.py
check "budget check passes the split configuration" bash -c "cd ch08-budget && python3 check-budget.py --ceiling 33000 --log runs/2026-11-05-budget-check/split-1.jsonl"
check "budget check fails the 146-line guide"       bash -c "cd ch08-budget && ! python3 check-budget.py --ceiling 33000 --log runs/2026-11-05-budget-check/monolithic-1.jsonl"

echo "chapter 9, knowledge server"
check "error code lookup"        bash -c "cd ch09-mcp/server && python3 cli.py error-code E4021 | grep -q 'authorization expired'"
check "unknown code suggests neighbours" bash -c "cd ch09-mcp/server && python3 cli.py error-code E4023 | grep -q E4022"
check "schema hides secret values" bash -c "cd ch09-mcp/server && python3 cli.py config-schema payments | grep -q 'value not shown'"
check "data scoping hides restricted section" bash -c "cd ch09-mcp/server && KB_IDENTITY=engineer python3 cli.py architecture 'fraud scoring' | grep -q 'No architecture sections'"
if python3 -c "import mcp.server" 2>/dev/null; then
  check "server lists three tools" bash -c "cd ch09-mcp/server && python3 -c 'import asyncio,server;assert len(asyncio.run(server.mcp.list_tools()))==3'"
  check "HTTP gates hold" bash -c 'cd ch09-mcp && python3 tools/make-test-tokens.py >/dev/null && { python3 server/http_server.py >/dev/null 2>&1 & P=$!; sleep 3; python3 tools/check-gates.py | grep -q "all gates hold"; r=$?; kill -9 $P; exit $r; }'
  check "tool interface unchanged" bash -c "cd ch09-mcp && python3 tools/check-interface.py"
else
  echo "  skip  chapter 9 server checks need the MCP SDK (pip install \"mcp>=2.2,<3\")"
fi

echo "chapter 10, knowledge graph"
check "extraction builds the graph" bash -c "cd ch10-graph/graph && python3 extract.py | grep -q 'nodes'"
check "multi-hop traversal finds RenewalsWorker" bash -c "cd ch10-graph/graph && python3 query.py dependents NotificationsAPI 3 | grep -q RenewalsWorker"
check "config blast radius"         bash -c "cd ch10-graph/graph && python3 query.py config PAYMENT_API_KEY | grep -q PaymentsService"
check "benchmark harness runs"      bash -c "cd ch10-graph/eval && python3 run_graph_side.py | grep -q '10/10'"
check "refresh matches a rebuild"   bash -c "cd ch10-graph/eval && python3 check_refresh.py"
check "extraction guards fire"      bash -c "cd ch10-graph/eval && python3 check_guards.py"
check "graph matches the deployment manifest" bash -c "cd ch10-graph && python3 graph/extract.py >/dev/null && python3 eval/check_manifest.py"
check "extraction refuses credentials" bash -c "cd ch10-graph && python3 eval/check_secrets.py"

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
  check "catalog revision recorded"     bash -c "cd ch11-catalog && python3 validate.py --check-revision"
  check "SQL hook blocks and allows its fixtures" bash -c "cd ch11-catalog && python3 eval/check_hook.py"
else
  echo "  skip  chapter 11 needs PyYAML (pip install pyyaml)"
fi

echo "chapter 12, retrieval router"
check "router routes 36/42 by rules; evidence checker and log redaction hold" bash -c "cd ch12-router/eval && python3 check_router.py"
if python3 -c "import mcp.server, numpy, yaml" 2>/dev/null; then
  check "knowledge server wraps every path in an evidence envelope" bash -c "cd ch12-router/eval && python3 check_server.py"
fi

echo "chapter 13, desktop port"
if python3 -c "import mcp.server, yaml" 2>/dev/null; then
  check "connector passes the sign-in checks" bash -c 'cd ch13-desktop-port && { python3 connector/server.py >/dev/null 2>&1 & P=$!; sleep 3; python3 tools/connector-check.py | grep -q "all checks pass"; r=$?; kill -9 $P; exit $r; }'
  check "plugin ships no credentials" bash -c "! grep -qiE 'authorization|bearer|token|api[-_ ]?key' ch13-desktop-port/marketplace/plugins/governed-data/.mcp.json"
  check "plugin skill keeps to the spec fields" bash -c "python3 -c \"import yaml,sys; f=open('ch13-desktop-port/marketplace/plugins/governed-data/skills/answer-with-governed-data/SKILL.md').read().split('---')[1]; sys.exit(not set(yaml.safe_load(f)) <= {'name','description','license','compatibility','metadata','allowed-tools'})\""
else
  echo "  skip  chapter 13 needs PyYAML and the MCP SDK"
fi

echo "chapter 14, observability"
if python3 -c "import mcp.server, opentelemetry.sdk, opentelemetry.proto" 2>/dev/null; then
  check "ch14 traversal spans record coverage"  bash -c "cd ch14-observability && python3 tools/check-instrumentation.py"
  check "ch14 collector hashes identity"        bash -c 'cd ch14-observability && T=$(mktemp -d) && { python3 collector.py --out "$T" 2>/dev/null & P=$!; sleep 1; python3 tools/check-collector.py "$T"; r=$?; kill $P; rm -rf "$T"; exit $r; }'
  check "ch14 triage verdicts unchanged"        bash -c "cd ch14-observability && python3 eval/check-saved-runs.py"
  check "ch14 access policy holds"              bash -c "cd ch14-observability && python3 policy.py access runs/2026-11-05-access/*"
else
  echo "  skip  chapter 14 needs the MCP SDK and OpenTelemetry (pip install -r ch14-observability/requirements.txt)"
fi
check "ch14 audit hook redacts secrets"         bash ch14-observability/tools/check-redaction.sh

echo "chapter 15, governed workflow"
if python3 -c "import mcp.server, yaml, numpy" 2>/dev/null; then
  check "gate guarantees hold"                 bash -c "cd ch15-governed-workflow && python3 eval/check_gate.py"
  check "published traces are complete"        bash -c "cd ch15-governed-workflow && python3 eval/check_trace.py runs/2026-11-05-*/claude-*"
  check "published runs grade as reported"     bash -c "cd ch15-governed-workflow && python3 eval/grade.py runs/2026-11-05-matrix/*/ runs/2026-11-05-scaled/*/ runs/2026-11-05-final/*/"
  check "onboarding passes the manifest check" bash -c "bash ch15-governed-workflow/scale/onboard.sh | grep -q 'graph matches the manifest: 11 services'"
else
  echo "  skip  chapter 15 needs the MCP SDK, PyYAML, and numpy"
fi
if command -v ags-validate >/dev/null; then
  check "change-config graph validates"      ags-validate --strict --quiet ch15-governed-workflow/graph/change-config.agraph.yaml
fi
if command -v claude >/dev/null; then
  check "governed-change plugin installs"    bash ch15-governed-workflow/eval/check-install.sh
fi

echo "appendix A, AGS"
if command -v ags-validate >/dev/null 2>&1; then
  check "AGS graph validates strictly"    ags-validate --strict --quiet ags/migrate-order-service.agraph.yaml
  check "AGS digest matches the appendix" python3 -c "import ags,yaml;d=yaml.safe_load(open('ags/migrate-order-service.agraph.yaml'));assert ags.graph_digest(d)=='sha256-5XVb3axq6g9HuExsesW5zrcZKeBd53y+D8e7xNFadiI='"
else
  echo "  skip  appendix A needs the reference validator (pip install agentic-graph-spec==1.0.4)"
fi

echo
echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
