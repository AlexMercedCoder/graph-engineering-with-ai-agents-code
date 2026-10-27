# Resuming a subagent

Step 1 delegated the failing test suite to `test-runner`, as in `../2026-10-27-isolation/`. Step 2,
in the same session: `Resume that same test-runner subagent (don't start a new one) and ask it: of
the failures you found, which one would you fix first, and why? Relay its answer.`

In both runs the main session loaded `SendMessage` and sent the question to the worker's agent ID.
The worker answered in one request, from the context of its first run (payloads of 15,814 and
18,800 tokens), without running the tests again, and both picked the `findByEmail` soft-delete
failure in `src/services/auth-service.js`.
