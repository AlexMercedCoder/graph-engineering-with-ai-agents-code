#!/usr/bin/env python3
"""trace-stdio.py LOG -- COMMAND...: run a stdio MCP server and log every message.

Register this in place of the server command to watch what your harness sends:

    "args": ["tools/trace-stdio.py", "/tmp/kb-trace.jsonl", "--", "python3", "server/server.py"]

Each log line is {"dir": "->" (harness to server) or "<-", "msg": ...}.
"""
import json
import subprocess
import sys
import threading

log_path, cmd = sys.argv[1], sys.argv[sys.argv.index("--") + 1:]
log = open(log_path, "a", buffering=1)
lock = threading.Lock()
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def pump(src, dst, direction):
    for line in src:
        with lock:
            try:
                log.write(json.dumps({"dir": direction, "msg": json.loads(line)}) + "\n")
            except ValueError:
                log.write(json.dumps({"dir": direction, "raw": line.decode(errors="replace")}) + "\n")
        dst.write(line)
        dst.flush()
    if direction == "->":
        proc.stdin.close()


threading.Thread(target=pump, args=(sys.stdin.buffer, proc.stdin, "->"), daemon=True).start()
pump(proc.stdout, sys.stdout.buffer, "<-")
sys.exit(proc.wait())
