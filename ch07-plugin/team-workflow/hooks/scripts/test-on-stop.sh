#!/usr/bin/env bash
set -euo pipefail

cat >/dev/null

# Only run the suite when source actually changed this session.
if ! git diff --quiet -- 'src/**' 2>/dev/null; then
  ATTEMPTS_FILE="${TMPDIR:-/tmp}/agent-stop-attempts"
  attempts=$(cat "$ATTEMPTS_FILE" 2>/dev/null || echo 0)
  if ! npm test --silent >"${TMPDIR:-/tmp}/agent-test.log" 2>&1; then
    attempts=$((attempts + 1))
    echo "$attempts" > "$ATTEMPTS_FILE"
    if [[ "$attempts" -ge 3 ]]; then
      rm -f "$ATTEMPTS_FILE"
      echo "Tests still failing after $attempts attempts. Letting the session end." >&2
      exit 0
    fi
    echo "Tests fail. Source files changed this session, so the work is not done." >&2
    echo "Failing output:" >&2
    tail -n 25 "${TMPDIR:-/tmp}/agent-test.log" >&2
    exit 2
  fi
  rm -f "$ATTEMPTS_FILE"
fi

exit 0
