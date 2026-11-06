#!/usr/bin/env bash
# Every scenario in both harnesses, N runs each, one at a time (they share ports).
#   bash run-matrix.sh <out-dir> [runs]
set -uo pipefail
out=${1:?usage: run-matrix.sh <out-dir> [runs]}; n=${2:-2}
here=$(cd "$(dirname "$0")" && pwd)
for run in $(seq 1 "$n"); do
  for scenario in fix-approve fix-reject fix-timeout no-evidence staging-fix; do
    for harness in claude opencode; do
      python3 "$here/run.py" --harness "$harness" --scenario "$scenario" --run "$run" --out "$out" \
        || echo "run failed: $harness $scenario $run"
    done
  done
done
python3 "$here/grade.py" "$out"/*/
