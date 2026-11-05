#!/usr/bin/env python3
"""Build the Chapter 11 sample warehouse: ten insurance tables in one SQLite file.

    python3 warehouse/seed.py            # writes warehouse/warehouse.db
    python3 warehouse/seed.py --schema   # prints the DDL only

The data is generated from a fixed seed, so every reader gets the same numbers.
Four of the ten tables are deliberately left out of catalog.yaml: a legacy
premium snapshot, a raw staging copy, a policyholder table with personal data,
and a date dimension. They are the tables a real warehouse accumulates, and the
ones an agent reading the raw schema has to decide about.
"""
import argparse
import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "warehouse.db"

DDL = """
CREATE TABLE dim_geography (geo_id INTEGER PRIMARY KEY, region TEXT, territory TEXT);
CREATE TABLE dim_product (product_id INTEGER PRIMARY KEY, product_line TEXT, distribution_channel TEXT);
CREATE TABLE dim_agent (agent_id INTEGER PRIMARY KEY, agent_name TEXT, geo_id INTEGER);
CREATE TABLE dim_policyholder (holder_id INTEGER PRIMARY KEY, policy_id INTEGER, holder_name TEXT, email TEXT, segment TEXT);
CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, month TEXT, quarter TEXT, year INTEGER);
CREATE TABLE fct_policy_premium (premium_id INTEGER PRIMARY KEY, policy_id INTEGER, geo_id INTEGER, product_id INTEGER, agent_id INTEGER, premium_amt REAL, premium_amt_gross REAL, cancellation_amt REAL, status TEXT, eff_dt TEXT);
CREATE TABLE fct_claims (claim_id INTEGER PRIMARY KEY, policy_id INTEGER, claim_amt REAL, paid_amt REAL, status TEXT, severity TEXT, reported_dt TEXT, closed_dt TEXT);
CREATE TABLE fct_commissions (commission_id INTEGER PRIMARY KEY, agent_id INTEGER, premium_id INTEGER, commission_amt REAL, paid_dt TEXT);
CREATE TABLE fct_premiums_v1 (pol_id INTEGER, region_name TEXT, prem REAL, eff_date TEXT);
CREATE TABLE stg_premium_raw (load_id INTEGER, premium_id INTEGER, policy_id INTEGER, geo_id INTEGER, product_id INTEGER, premium_amt REAL, cancellation_amt REAL, status TEXT, eff_dt TEXT);
""".strip()

REGIONS = {"North America": ["US East", "US West"], "EMEA": ["UK", "DACH"],
           "APAC": ["ANZ", "Japan"], "LATAM": ["Brazil", "Mexico"]}
PRODUCTS = [(line, ch) for line in ("Auto", "Home", "Commercial") for ch in ("Direct", "Broker")]
START, END = date(2025, 1, 1), date(2026, 10, 31)


def build(path):
    rng = random.Random(11)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript(DDL)

    geos = [(i, r, t) for i, (r, t) in enumerate(
        ((r, t) for r, ts in REGIONS.items() for t in ts), start=1)]
    con.executemany("INSERT INTO dim_geography VALUES (?,?,?)", geos)
    con.executemany("INSERT INTO dim_product VALUES (?,?,?)",
                    [(i, l, c) for i, (l, c) in enumerate(PRODUCTS, start=1)])
    agents = [(i, f"Agent {i:02d}", rng.randint(1, len(geos))) for i in range(1, 25)]
    con.executemany("INSERT INTO dim_agent VALUES (?,?,?)", agents)

    d = START
    while d <= END:
        q = (d.month - 1) // 3 + 1
        con.execute("INSERT INTO dim_date VALUES (?,?,?,?)",
                    (d.isoformat(), d.strftime("%Y-%m"), f"{d.year}-Q{q}", d.year))
        d += timedelta(days=1)

    days = (END - START).days
    premiums, commissions, claims, holders = [], [], [], []
    pid = cid = clid = 0
    for policy_id in range(1, 2601):
        geo = rng.randint(1, len(geos))
        # an agent from the policy's region most of the time, from elsewhere otherwise
        local = [a for a in agents if a[2] == geo]
        agent = rng.choice(local) if local and rng.random() < 0.7 else rng.choice(agents)
        product = rng.randint(1, len(PRODUCTS))
        eff = START + timedelta(days=rng.randint(0, days))
        status = rng.choices(["written", "cancelled", "quote"], [0.72, 0.08, 0.20])[0]
        amt = round(rng.uniform(400, 6000) * (2.5 if PRODUCTS[product - 1][0] == "Commercial" else 1), 2)
        gross = round(amt * 1.12, 2)
        canc = round(amt * rng.uniform(0.3, 1.0), 2) if status == "cancelled" else 0.0
        pid += 1
        premiums.append((pid, policy_id, geo, product, agent[0], amt, gross, canc, status, eff.isoformat()))
        if status != "quote":
            holders.append((policy_id, policy_id, f"Holder {policy_id:04d}",
                            f"holder{policy_id:04d}@example.com", rng.choice(["Retail", "SME", "Corporate"])))
            cid += 1
            paid = eff + timedelta(days=rng.randint(10, 45))
            if paid <= END:
                commissions.append((cid, agent[0], pid, round(amt * 0.08, 2), paid.isoformat()))
            if rng.random() < 0.18:
                clid += 1
                rep = eff + timedelta(days=rng.randint(5, 200))
                if rep <= END:
                    sev = rng.choices(["Low", "Medium", "High"], [0.6, 0.3, 0.1])[0]
                    claimed = round({"Low": 800, "Medium": 4000, "High": 15000}[sev] * rng.uniform(0.5, 1.5), 2)
                    closed = rep + timedelta(days=rng.randint(10, 120))
                    if closed <= END and rng.random() < 0.8:
                        claims.append((clid, policy_id, claimed, round(claimed * rng.uniform(0.6, 1.0), 2),
                                       "closed", sev, rep.isoformat(), closed.isoformat()))
                    else:
                        claims.append((clid, policy_id, claimed, round(claimed * rng.uniform(0, 0.4), 2),
                                       "open", sev, rep.isoformat(), None))

    con.executemany("INSERT INTO fct_policy_premium VALUES (?,?,?,?,?,?,?,?,?,?)", premiums)
    con.executemany("INSERT INTO fct_commissions VALUES (?,?,?,?,?)", commissions)
    con.executemany("INSERT INTO fct_claims VALUES (?,?,?,?,?,?,?,?)", claims)
    con.executemany("INSERT INTO dim_policyholder VALUES (?,?,?,?,?)", holders)

    # Legacy snapshot: 2025 only, taken before late cancellations were booked.
    region_of = {g[0]: g[1] for g in geos}
    con.executemany("INSERT INTO fct_premiums_v1 VALUES (?,?,?,?)",
                    [(p[1], region_of[p[2]], p[5], p[9]) for p in premiums
                     if p[9] < "2026-01-01" and p[8] != "quote"])
    # Raw staging: every load appends, so recent rows appear twice.
    raw = [(1,) + (p[0], p[1], p[2], p[3], p[5], p[7], p[8], p[9]) for p in premiums]
    raw += [(2,) + (p[0], p[1], p[2], p[3], p[5], p[7], p[8], p[9]) for p in premiums if p[9] >= "2026-07-01"]
    con.executemany("INSERT INTO stg_premium_raw VALUES (?,?,?,?,?,?,?,?,?)", raw)
    con.commit()
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con.close()
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", action="store_true", help="print the DDL and exit")
    ap.add_argument("--out", type=Path, default=DB)
    a = ap.parse_args()
    if a.schema:
        print(DDL)
        return 0
    counts = build(a.out)
    print(f"Wrote {a.out.name}: {len(counts)} tables")
    for t, n in counts.items():
        print(f"  {t:20} {n:6} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
