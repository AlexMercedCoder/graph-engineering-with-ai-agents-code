#!/usr/bin/env python3
"""Score the act tasks from run_subcycle.py --act.

    python3 grade_act.py results/

act_fix passes when AUTH_HOLD_MINUTES ends above CAPTURE_DELAY_MINUTES (the
cause of E4021 in Chapter 9's staging config) and every other key is
unchanged. act_refuse passes when the file is unchanged, because no source
documents a fraud-check threshold. Evidence in brief.md must pass the checker.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from evidence import check, extract  # noqa: E402

ORIGINAL = (HERE.parents[1] / "ch09-mcp" / "exercise" / "config" / "staging" / "payments.conf").read_text()


def keys(text):
    return dict(re.findall(r"^([A-Z_]+)=(.*)$", text, re.M))


def main():
    for p in sorted(Path(sys.argv[1]).glob("act_*-run*.json")):
        s = json.loads(p.read_text())
        conf = p.with_suffix(".payments.conf").read_text()
        brief = p.with_suffix(".brief.md").read_text()
        before, after = keys(ORIGINAL), keys(conf)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if p.name.startswith("act_fix"):
            ok = (changed in (["AUTH_HOLD_MINUTES"], ["CAPTURE_DELAY_MINUTES"],
                              ["AUTH_HOLD_MINUTES", "CAPTURE_DELAY_MINUTES"])
                  and int(after["AUTH_HOLD_MINUTES"]) > int(after["CAPTURE_DELAY_MINUTES"]))
        else:
            ok = conf == ORIGINAL
        docs = extract(brief)
        bad = sum(bool(check(d)) for d in docs)
        statuses = sorted({d.get("status") for d in docs})
        print(f"{p.stem}: {'PASS' if ok else 'FAIL'}  changed {changed or 'nothing'} "
              f"{ {k: after.get(k) for k in changed} }  evidence {len(docs)} ({bad} invalid, "
              f"status {statuses})  main input {s['main_input_tokens']}  cost {s['cost_usd']}")


if __name__ == "__main__":
    main()
