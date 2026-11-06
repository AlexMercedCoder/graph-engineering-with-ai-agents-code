#!/usr/bin/env python3
"""Reset the deployed configurations from Chapter 9's exercise, optionally with a fault.

    python3 seed-deploy.py                         staging and production as Chapter 9 ships them
    python3 seed-deploy.py --fault production      AUTH_HOLD_MINUTES=10 in production
    python3 seed-deploy.py --fault both            ... and in staging

AUTH_HOLD_MINUTES=10 is below CAPTURE_DELAY_MINUTES=15, so authorization
holds lapse before capture and captures fail with E4021. It also clears the
approval store and the decision log.
"""
import argparse
import os
import re
import shutil
from pathlib import Path

CH15 = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get("GOVERNED_STATE", CH15 / "state"))
SOURCE = CH15.parent / "ch09-mcp" / "exercise" / "config"

ap = argparse.ArgumentParser()
ap.add_argument("--fault", choices=["none", "production", "both"], default="none")
a = ap.parse_args()
for sub in ("deploy", "approvals"):
    shutil.rmtree(STATE / sub, ignore_errors=True)
for f in ("decisions.jsonl", "seen-packets.jsonl"):
    (STATE / f).unlink(missing_ok=True)
for env in ("staging", "production"):
    (STATE / "deploy" / env).mkdir(parents=True)
    text = (SOURCE / env / "payments.conf").read_text()
    if a.fault == "both" or a.fault == env:
        text = re.sub(r"^AUTH_HOLD_MINUTES=.*$", "AUTH_HOLD_MINUTES=10", text, flags=re.M)
    (STATE / "deploy" / env / "payments.conf").write_text(text)
print(f"seeded {STATE / 'deploy'} (fault: {a.fault})")
