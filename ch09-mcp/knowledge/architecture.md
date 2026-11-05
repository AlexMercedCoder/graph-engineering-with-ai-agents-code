## Service map
The platform is eight services behind one gateway. The gateway terminates TLS,
applies rate limits, and forwards to users, auth, orders, payments,
notifications, reporting, and search. Services call each other over internal
HTTP with the caller's session token forwarded only to the users and auth
services; every other internal call uses the calling service's own credential.
Orders calls payments to authorize and capture, payments calls notifications
when a capture succeeds or fails, and reporting reads a replica of the orders
and payments databases rather than calling either service.
classification: internal

## Order lifecycle
An order starts as a quote. Adding a payment authorization moves it to pending.
Capture moves it to paid. Only paid orders appear in revenue reports, which is why
the paid-total report filters on status rather than on the presence of a payment row.
A cancelled order keeps its rows; cancellation releases any inventory reservation
and voids an uncaptured authorization.
classification: internal

## Authorization and capture
Payments authorizes when the order moves to pending and captures later, from the
capture worker, CAPTURE_DELAY_MINUTES after authorization. The delay exists so that
an order edited within a few minutes of checkout can be re-authorized without a
refund. The provider holds an authorization for AUTH_HOLD_MINUTES; a hold that
lapses before the worker captures produces E4021 on capture. Capture is idempotent
by order id, so a second capture of the same order returns E5011 and is treated as
success. Captures that fail with a retryable provider error are retried up to
MAX_CAPTURE_RETRIES times with exponential backoff.
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

## Session handling
The auth service signs session tokens with SIGNING_KEY and accepts tokens signed
with SIGNING_KEY_PREVIOUS during a rotation. Tokens expire after
SESSION_TTL_MINUTES. A revoked session is recorded in the users database and
checked on every request by the gateway, which is why revocation takes effect
immediately rather than at expiry.
classification: internal

## Reporting replica
Reporting reads from a read replica that normally trails the primary by a few
seconds. When lag passes STALENESS_BANNER_SECONDS, reports carry a staleness
banner instead of failing. Long ranges should use the precomputed daily tables,
which are rebuilt at 02:00 UTC.
classification: internal

## Search indexing
Search indexes orders and users. Writes reach the index through an outbox table
that a worker drains in REINDEX_BATCH batches, so search results can trail the
database by up to a minute. A full reindex writes to a new index with the
INDEX_PREFIX and swaps an alias when it finishes.
classification: internal

## Configuration and secrets
Each service reads its configuration from environment variables at startup and
refuses to start when a required key is missing (E9002) or invalid (E9003).
Non-secret values for each environment live in config/<environment>/<service>.conf
in the repository. Secret values come from the secrets manager at deploy time and
are never committed.
classification: internal

## Fraud scoring thresholds
Orders are scored on four signals: velocity (orders per card per hour), a
mismatch between billing and shipping country, account age, and the amount.
The weights are 0.35, 0.25, 0.20, and 0.20. An order scoring above 0.82, or any
order above 2,500 USD on an account younger than seven days, is held for manual
review. Orders scoring between 0.65 and 0.82 are captured but flagged for a
next-day audit.
classification: restricted

## Signing key rotation procedure
Rotation runs quarterly. The new key is written to SIGNING_KEY and the old one to
SIGNING_KEY_PREVIOUS, both services are restarted in order (auth, then gateway),
and SIGNING_KEY_PREVIOUS is cleared after SESSION_TTL_MINUTES have passed. The
secrets manager path for the keys is security/auth/signing.
classification: restricted
