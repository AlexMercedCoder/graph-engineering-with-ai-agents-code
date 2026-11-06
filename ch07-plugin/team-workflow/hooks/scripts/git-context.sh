#!/usr/bin/env bash
set -euo pipefail

branch=$(git branch --show-current 2>/dev/null) || exit 0
changes=$(git status --porcelain 2>/dev/null)

echo "Git state at this prompt: branch ${branch:-(detached HEAD)}, $(grep -c . <<<"$changes" || true) uncommitted file(s)."
[[ -n "$changes" ]] && head -n 10 <<<"$changes"
exit 0
