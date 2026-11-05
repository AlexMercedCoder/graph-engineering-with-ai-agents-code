# Deterministic checks (2026-11-03)

`output.txt` is `bash eval/checks.sh` from `ch11-catalog/` with Python 3.14.5, PyYAML 6.0.3, and
MCP Python SDK 2.0.0. No agent is involved, so one run is enough; rerun it to compare.

| Step | Shows |
|---|---|
| 1 | A valid request (net written premium by region, 2026-Q3) compiles to SQL |
| 2 | An invalid dimension and a day-level range are refused with the valid choices |
| 3 | A hand-written query with six mistakes gets six rejections; a comma join and a quoted table name are caught too |
| 4 | Compiled SQL returns the same numbers as hand-written SQL for q1 to q4 |
| 5 | `navigate_catalog` hides `commission_paid` from `analyst` and shows it to `finance` |
| 6 | `emea-analyst` gets only the EMEA row for the same signed request |
| 7 | The executor refuses hand-written SQL, edited generated SQL, and SQL from an older catalog revision |
| 8 | With `catalog:read` alone the server registers two tools; with `data:read` too, three |
| 9 | The row cap truncates a 22-month result at the requested five rows |
