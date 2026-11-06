"""Times each hook script on a sample event: python3 bench.py, run from a copy of sample-project/.

Prints the median and 95th percentile of 200 runs per script, after 10 warm-up runs.
"""
import json, statistics, subprocess, time
from pathlib import Path

here = Path(__file__).resolve().parent
scripts = here.parents[2] / "scripts"
event = lambda e, t, i: json.dumps({"session_id": "s", "hook_event_name": e, "tool_name": t, "tool_input": i}).encode()
write = event("PreToolUse", "Write", {"file_path": "src/services/order-service.js", "content": "x"})
bash = event("PreToolUse", "Bash", {"command": "npm test"})
edit = event("PostToolUse", "Edit", {"file_path": "src/services/order-service.js"})
empty = here / "empty.sh"
empty.write_text("#!/usr/bin/env bash\ncat >/dev/null\nexit 0\n"); empty.chmod(0o755)

cases = [
    ("empty bash script", empty, write),
    ("protect-paths.sh (1 jq)", scripts / "protect-paths.sh", write),
    ("guard-bash.sh (1 jq)", scripts / "guard-bash.sh", bash),
    ("confirm-destructive-sql.sh (1 jq)", scripts / "confirm-destructive-sql.sh", bash),
    ("audit.sh (1 jq)", scripts / "audit.sh", bash),
    ("git-context.sh (2 git)", scripts / "git-context.sh", bash),
    ("lint-on-edit.sh (jq + node)", scripts / "lint-on-edit.sh", edit),
]
for name, path, data in cases:
    for _ in range(10):
        subprocess.run([path], input=data, capture_output=True)
    times = []
    for _ in range(200):
        t = time.perf_counter()
        subprocess.run([path], input=data, capture_output=True)
        times.append((time.perf_counter() - t) * 1000)
    times.sort()
    print(f"{name:36s} median {statistics.median(times):6.1f} ms  p95 {times[189]:6.1f} ms")
