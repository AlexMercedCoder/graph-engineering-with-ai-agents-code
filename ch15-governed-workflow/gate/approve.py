#!/usr/bin/env python3
"""The reviewer's side of the gate.

    python3 approve.py list
    python3 approve.py show apr_1a2b3c
    python3 approve.py approve apr_1a2b3c --as dana
    python3 approve.py reject apr_1a2b3c --as dana --reason "Staging first."

Each decision is signed with the reviewer's key from config/reviewers.json,
which stands in for the credential your identity provider would check.
"""
import argparse
import sys
import time

import approvals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["list", "show", "approve", "reject"])
    ap.add_argument("request_id", nargs="?")
    ap.add_argument("--as", dest="reviewer")
    ap.add_argument("--reason", default="")
    a = ap.parse_args()
    if a.command == "list":
        for r in approvals.pending():
            left = r["expires_epoch"] - int(time.time())
            print(f"{r['id']}  {r['action']['environment']} {r['action']['key']} "
                  f"{r['action']['from']} -> {r['action']['to']}  ({left}s left)")
        return
    try:
        req = approvals.load(a.request_id)
    except ValueError as e:
        sys.exit(str(e))
    if a.command == "show":
        print(req["packet"])
        print(f"\nstatus {req['status']}, roles {req['roles']}, digest {req['action_digest']}")
        return
    if req["status"] != "pending" or req["expires_epoch"] <= time.time():
        sys.exit(f"{a.request_id} is {req['status']} and can't be decided now.")
    if a.command == "reject" and not a.reason:
        sys.exit("A rejection needs --reason, so the agent can tell the user what to do instead.")
    if not a.reviewer:
        sys.exit("Say who is deciding: --as <reviewer>.")
    signed = approvals.decide(a.request_id, a.command, a.reviewer, a.reason)
    print(f"{signed['decision']} filed for {a.request_id} by {a.reviewer}")


if __name__ == "__main__":
    main()
