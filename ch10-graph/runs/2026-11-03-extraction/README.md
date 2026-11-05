# Extraction

`python3 extract.py --model --rebuild` over the ten documents, `claude-sonnet-5-5` through
`claude -p` (Claude Code 2.1.316), twice with each ontology. Each JSON file is the saved model reply
for one document with its token use and cost.

| Run | Relationship types | Model calls | Cost | Edges after validation | Documented edges | Missed | Dropped by guards |
|---|---|---|---|---|---|---|---|
| four-types-run1 | 4 | 10 | $0.1599 | 26 | 27 | `GATEWAY_RATE_LIMITS -CONFIGURES-> ApiGateway` | 0 |
| four-types-run2 | 4 | 10 | $0.1624 | 26 | 27 | same | 0 |
| five-types-run1 | 5 | 10 (76 s) | $0.1656 | 30 | 31 | same | 0 |
| five-types-run2 | 5 | 10 (82 s) | $0.1751 | 30 | 31 | same | 0 |

No run produced a relationship type outside the ontology or an edge whose quote was missing from
its document. The four traps in the documents (the shared on-call rotation, the shared team, the
hand-copied dashboard figures, and `ORDER_DB_URL` configuring UserService) produced no edges.

Entity names differed. With four types, run 1 named the payments and users databases `payments`
and `users`, run 2 named the orders and users databases `orders` and `users`, and the rest by full
description; the three aliases in `ontology.py` make both runs build identical graphs. With five
types, both runs listed an entity `gateway` from user-service.md ("the session tokens that the
gateway forwards"), which the `gateway` alias folds into ApiGateway. `graph/extractions/` holds
five-types-run1.
