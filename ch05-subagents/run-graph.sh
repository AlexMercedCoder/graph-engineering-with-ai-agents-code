#!/usr/bin/env bash
# The execution graph from Chapter 5's "Running the graph without subagents".
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
PROJECT="${PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)/sample-project}"
AGENT_CMD="${AGENT_CMD:-}"
NODES="$(cd "$(dirname "$0")" && pwd)/nodes"

cd "$PROJECT"
[[ -n "$AGENT_CMD" ]] && mkdir -p .agent-work

# run_node <brief> [VAR=value ...] [input-file ...]: one fresh session per node. Values and
# input files are appended to the brief, so the node sees only what it declares.
run_node() {
  local brief="$1"; shift
  if [[ -z "$AGENT_CMD" ]]; then
    echo "--- DRY RUN: would run node $(basename "$brief") in a fresh session"
    echo "    inputs: $*"
    return 0
  fi
  {
    cat "$brief"
    for arg in "$@"; do
      if [[ "$arg" == *=* ]]; then echo; echo "${arg%%=*}: ${arg#*=}"
      else echo; echo "--- input: $arg"; cat "$arg"; fi
    done
  } | $AGENT_CMD
}

echo "== node 1: run-tests"
run_node "$NODES/01-run-tests.md"
if [[ -n "$AGENT_CMD" && ! -f .agent-work/test-failures.md ]]; then
  echo "run-tests did not satisfy its success condition (no output file)" >&2; exit 1
fi

echo "== node 2: migrate-module ($MODULE)"
run_node "$NODES/02-migrate-module.md" "MODULE=$MODULE"
base=$(basename "$MODULE" .js)
if [[ -n "$AGENT_CMD" ]]; then
  node --test "tests/${base}.test.js" || { echo "migrate-module did not satisfy its success condition (module tests)" >&2; exit 1; }
  node scripts/check-routes.js || { echo "migrate-module did not satisfy its success condition (routes)" >&2; exit 1; }
fi

echo "== node 3: verify"
run_node "$NODES/03-verify.md"
if [[ -z "$AGENT_CMD" ]]; then echo "== dry run complete (no node ran, no check ran)"; exit 0; fi
npm test --silent || { echo "verify failed: the full suite does not pass" >&2; exit 1; }
node scripts/check-routes.js || { echo "verify failed: a route does not respond" >&2; exit 1; }
echo "== graph complete"
