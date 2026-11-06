#!/usr/bin/env python3
"""A scripted reviewer for the evaluation runs, standing in for a person.

    python3 reviewer.py approve
    python3 reviewer.py reject "Apply it to staging first; production waits for the change window."
    python3 reviewer.py ignore

It decides every pending request the same way, after reading for
REVIEW_DELAY seconds (default 5), and signs as the test reviewer. It saves
each packet it saw, so a run can check what the reviewer was shown.
"""
import json
import os
import sys
import time

import approvals

REVIEWER = "test-reviewer"


def main():
    policy = sys.argv[1]
    reason = sys.argv[2] if len(sys.argv) > 2 else ""
    delay = float(os.environ.get("REVIEW_DELAY", 5))
    seen = set()
    while True:
        for req in approvals.pending():
            if req["id"] in seen:
                continue
            seen.add(req["id"])
            with (approvals.STATE / "seen-packets.jsonl").open("a") as f:
                f.write(json.dumps({"id": req["id"], "packet": req["packet"]}) + "\n")
            if policy == "ignore":
                continue
            time.sleep(delay)
            approvals.decide(req["id"], policy, REVIEWER, reason)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
