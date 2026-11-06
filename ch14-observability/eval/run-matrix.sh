#!/usr/bin/env bash
# Every condition in both harnesses, N runs each (default 3), into <runs-dir>.
# Skips a run whose folder already has triage.json. HARNESSES limits the harnesses.
#   bash eval/run-matrix.sh <runs-dir> [N]
set -uo pipefail
dir=${1:?usage: run-matrix.sh <runs-dir> [N]}; n=${2:-3}
here=$(cd "$(dirname "$0")" && pwd)
for i in $(seq 1 "$n"); do
  for c in baseline bad-description depth-cap-silent depth-cap soft-body stale-rule; do
    for h in ${HARNESSES:-claude opencode}; do
      [ -f "$dir/$h-$c-$i/triage.json" ] && continue
      bash "$here/run.sh" "$h" "$c" "$dir/$h-$c-$i" | tail -1
    done
  done
done
python3 "$here/summarize.py" "$dir"
