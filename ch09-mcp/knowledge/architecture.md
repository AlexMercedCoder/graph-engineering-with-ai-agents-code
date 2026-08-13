## Order lifecycle
An order starts as a quote. Adding a payment authorization moves it to pending.
Capture moves it to paid. Only paid orders appear in revenue reports, which is why
the paid-total report filters on status rather than on the presence of a payment row.
classification: internal

## Soft deletes
Users are never hard-deleted. A deleted user keeps its row with a non-null
deleted_at, because orders reference users and reporting needs the history.
Every read path must filter deleted_at, and forgetting to is the single most
common bug in this codebase.
classification: internal

## Repository pattern
Services must not build queries. Each table has one repository class exposing
promise-returning methods. The services in src/services predate this rule and are
being migrated one module at a time.
classification: internal

## Notifications retry policy
The notifications service retries a failed webhook three times with a 250ms
backoff. Callers see success as soon as the webhook is queued, not when it is
delivered, which means a caller cannot infer delivery from a 200 response.
classification: internal

## Fraud scoring thresholds
Orders above the review threshold are held for manual review. The exact
thresholds and the weighting of the signals are commercially sensitive.
classification: restricted
