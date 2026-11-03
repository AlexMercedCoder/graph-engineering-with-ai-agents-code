# Chapter 4 boundary prompts, four more runs, 2026-11-03

The five prompts that sit between reporting and changing code (11, 13, 15, 16, 17 in
`../../eval/prompts.jsonl`), run four more times under version B (with the redirect clauses in
`code-review` and `fix-lint`) and version D (without them), in each harness. Together with runs 1
and 2 in `../2026-10-27-routing/`, each prompt has six sessions per version per harness.

- **Claude Code** 2.1.316, `claude-opus-5-5`; **OpenCode** 1.19.5, `openai/gpt-6.1-sol`. Same commands
  as the October runs: `PROMPT_IDS="11 13 15 16 17" bash ../../eval/run-routing.sh <harness> <b|d> <results>`.

First skill loaded, six sessions per cell (October runs 1 and 2 plus these runs 3 to 6):

| Prompt | Claude Code, B | Claude Code, D | OpenCode, B | OpenCode, D |
|---|---|---|---|---|
| 11 `Clean up src/services/payment-service.js` (expects fix-lint) | fix-lint 6 | fix-lint 6 | fix-lint 6 | fix-lint 6 |
| 13 `Can you look at the formatting in order-service.js?` (expects code-review) | none 6 | none 6 | code-review 6 | fix-lint 6 |
| 15 `Tidy up the services directory` (expects fix-lint) | fix-lint 2, none 4 | none 6 | fix-lint 6 | fix-lint 6 |
| 16 `Go through payment-service.js and tell me what you find` (expects code-review) | code-review 6 | code-review 6 | code-review 6 | code-review 6 |
| 17 `What should change in order-service.js?` (expects code-review) | code-review 6 | code-review 6 | code-review 6 | code-review 6 |

Files: `<harness>/results-<version>-run<n>.txt` and `<harness>/transcripts/<version>-<prompt>-<run>.jsonl`.
Claude Code `init` events are removed and local paths replaced with placeholders.
