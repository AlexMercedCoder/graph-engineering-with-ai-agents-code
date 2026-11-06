#!/usr/bin/env bash
# Test hook for Chapter 7: answers allow for the route check.
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in
  "node scripts/check-routes.js")
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"approved by test hook"}}' ;;
esac
exit 0
