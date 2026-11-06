#!/usr/bin/env python3
"""Commands the SQL hook must block and commands it must let through.

Add a line here whenever you change hooks/validate-sql.py or the catalog.
  python3 eval/check_hook.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "validate-sql.py"
BLOCK = [
    'sqlite3 warehouse.db "select * from fct_premiums_v1 limit 3"',
    'sqlite3 warehouse.db "select sum(commission_amt) from fct_commissions"',
    "sqlite3 warehouse.db 'select email from dim_policyholder'",
    "sqlite3 -header warehouse.db <<'SQL'\nselect count(*) from stg_premium_raw;\nSQL",
    'sqlite3 warehouse.db "select sum(premium_amt_gross) as gross_written_premium from fct_policy_premium"',
    # a comma inside the expression once hid it from the lineage check
    "sqlite3 warehouse.db \"select round(sum(premium_amt_gross), 2) as gross_written_premium from fct_policy_premium where status != 'quote'\"",
]
ALLOW = [
    'sqlite3 warehouse.db ".tables"',
    'sqlite3 warehouse.db "select region from dim_geography"',
    "sqlite3 warehouse.db \"select sum(premium_amt) as gross_written_premium from fct_policy_premium where status != 'quote'\"",
    'ls -la',
    # a common table expression is not an unknown table
    'sqlite3 warehouse.db "with prem as (select g.region, sum(p.premium_amt) amt from fct_policy_premium p join dim_geography g on g.geo_id = p.geo_id group by 1) select * from prem"',
]


def verdict(command):
    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = dict(os.environ, CATALOG_IDENTITY="analyst")
    return subprocess.run([sys.executable, str(HOOK)], input=event, text=True,
                          capture_output=True, env=env).returncode


failed = [("should block", c) for c in BLOCK if verdict(c) != 2]
# The hook fails closed: input it can't parse blocks the command instead of passing it.
broken = subprocess.run([sys.executable, str(HOOK)], input='{"tool_name": "Bash", ',
                        text=True, capture_output=True).returncode
if broken != 2:
    failed.append(("should fail closed", "malformed hook input"))
failed += [("should allow", c) for c in ALLOW if verdict(c) != 0]
for why, c in failed:
    print(f"{why}: {c!r}")
total = len(BLOCK) + len(ALLOW) + 1
print(f"{total - len(failed)} of {total} hook cases pass")
sys.exit(1 if failed else 0)
