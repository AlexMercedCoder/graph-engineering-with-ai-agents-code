#!/usr/bin/env bash
# The deterministic checks behind Chapter 11, one after another. No agent, no
# account; needs Python 3, PyYAML, and (for the scope check) the MCP SDK.
#
#   bash eval/checks.sh
set -uo pipefail
cd "$(dirname "$0")/.."
[ -f warehouse/warehouse.db ] || python3 warehouse/seed.py
export CATALOG_SCOPES="catalog:read data:read" CATALOG_IDENTITY=analyst
step() { echo; echo "== $*"; }

step "1. A valid request compiles to SQL"
python3 validate.py --metric net_written_premium --dimensions region --range 2026-Q3

step "2. An invalid dimension and a day-level range are refused"
python3 validate.py --metric net_written_premium --dimensions claim_severity --range 2026-03-15

step "3. Hand-written SQL through the four checks"
python3 validate.py --sql "SELECT g.product_line,
       SUM(p.premium_amt_gross) - SUM(p.cancellation_amt) AS net_written_premium
FROM analytics.fct_premiums x
JOIN analytics.fct_policy_premium p ON x.pol_id = p.policy_id
JOIN analytics.dim_geography g ON p.agent_id = g.geo_id
GROUP BY g.product_line, p.eff_dt"

echo "-- a comma join and a quoted name:"
python3 validate.py --sql "SELECT p.email FROM analytics.fct_policy_premium f, analytics.dim_policyholder p"
python3 validate.py --sql 'SELECT * FROM "fct_premiums_v1"'

step "4. Compiled SQL agrees with hand-written SQL on the four answerable questions"
python3 eval/truth.py --check

step "5. Navigation is filtered by identity"
echo "-- analyst:";  python3 server/cli.py navigate commission
echo "-- finance:";  CATALOG_IDENTITY=finance python3 server/cli.py navigate commission | head -3

step "6. The platform applies row policies: emea-analyst runs the same request"
CATALOG_IDENTITY=emea-analyst python3 server/cli.py ask net_written_premium region 2026-Q3 | tail -3

step "7. The executor refuses SQL that didn't come from the generator"
python3 server/cli.py execute --sql "SELECT SUM(premium_amt) FROM analytics.fct_policy_premium"
python3 - <<'PY'
import sys; sys.path.insert(0, "server")
import tools
sql = tools.generate_governed_sql("net_written_premium", ["region"], "2026-Q3")
edited = sql.replace("f.status != 'quote' AND ", "")
print("edited after generation:", tools.execute_query(edited))
orig = tools.Catalog
class Newer(orig):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.revision = "2026-11-04"
tools.Catalog = Newer
print("catalog changed since:  ", tools.execute_query(sql))
PY

step "8. Scopes decide which tools the server registers"
for s in "catalog:read" "catalog:read data:read"; do
  CATALOG_SCOPES="$s" python3 - <<'PY'
import asyncio, os, sys
sys.path.insert(0, "server")
import server
names = [t.name for t in asyncio.run(server.mcp.list_tools())]
print(f"scopes {os.environ['CATALOG_SCOPES']!r}: {', '.join(names)}")
PY
done

step "9. Row cap"
python3 - <<'PY'
import sys; sys.path.insert(0, "server")
import tools
sql = tools.generate_governed_sql("net_written_premium", ["policy_effective_month"], "2025-01..2026-10")
print(tools.execute_query(sql, max_rows=5))
PY
