#!/usr/bin/env bash
# The manual execution graph from Chapter 5's "If your harness lacks this".
# Every node runs in its own session with only its declared inputs, and every
# success condition is checked before the next node starts.
#
#   ./run-graph.sh src/services/user-service.js
#
# AGENT_CMD is whatever runs your harness non-interactively, reading a prompt on
# stdin. Examples:
#   AGENT_CMD="claude -p"
#   AGENT_CMD="codex exec"
set -euo pipefail

MODULE="${1:?usage: run-graph.sh src/services/<module>.js}"
PROJECT="${PROJECT_DIR:-../sample-project}"
AGENT_CMD="${AGENT_CMD:-}"
NODES="$(cd "$(dirname "$0")" && pwd)/nodes"

cd "$PROJECT"
mkdir -p .agent-work

run_node() {
  local brief="$1"; shift
  if [[ -z "$AGENT_CMD" ]]; then
    echo "--- DRY RUN: would run node $(basename "$brief") in a fresh session"
    echo "    inputs: $*"
    return 0
  fi
  { cat "$brief"; for f in "$@"; do echo; echo "--- input: $f"; cat "$f"; done; } | $AGENT_CMD
}

echo "== node 1: run-tests"
run_node "$NODES/01-run-tests.md"
if [[ -n "$AGENT_CMD" && ! -f .agent-work/test-failures.md ]]; then
  echo "run-tests did not satisfy its success condition (no output file)" >&2; exit 1
fi

echo "== node 2: migrate-module ($MODULE)"
MODULE="$MODULE" run_node "$NODES/02-migrate-module.md" .agent-work/test-failures.md 2>/dev/null || \
  run_node "$NODES/02-migrate-module.md"
base=$(basename "$MODULE" .js)
if [[ -n "$AGENT_CMD" ]]; then
  node --test "tests/${base}.test.js" || { echo "migrate-module did not satisfy its success condition" >&2; exit 1; }
fi

echo "== node 3: verify"
run_node "$NODES/03-verify.md"
npm test --silent || { echo "verify failed: the full suite does not pass" >&2; exit 1; }
echo "== graph complete"
