#!/usr/bin/env python3
"""Write the seven synthetic log files used by the Chapter 3 stress test into logs/.

Each file has 1,200 lines (about 43,000 tokens). The seed is fixed, so the files, and the
answers the stress test asks for, are the same on every machine. Run from sample-project/.
"""
import os
import random

random.seed(7)
levels = ["INFO"] * 18 + ["WARN"] * 3 + ["ERROR"]
services = ["api", "worker-1", "worker-2", "worker-3", "scheduler", "db-pool", "auth"]
messages = ["processed job {j} in {ms}ms", "cache miss for key order:{j}", "retrying request {j} after timeout",
            "connection {j} returned to pool", "user {j} session refreshed", "queue depth {ms}",
            "slow query on orders ({ms}ms)"]
os.makedirs("logs", exist_ok=True)
for n in range(1, 8):
    lines = []
    for i in range(1200):
        level = random.choice(levels)
        msg = random.choice(messages).format(j=random.randint(10000, 99999), ms=random.randint(3, 900))
        lines.append(f"2026-10-{10 + n:02d}T{i // 60 % 24:02d}:{i % 60:02d}:{random.randint(0, 59):02d}Z "
                     f"{level:5} {random.choice(services):10} {msg}")
    with open(f"logs/log-{n}.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
print("wrote logs/log-1.txt to logs/log-7.txt")
