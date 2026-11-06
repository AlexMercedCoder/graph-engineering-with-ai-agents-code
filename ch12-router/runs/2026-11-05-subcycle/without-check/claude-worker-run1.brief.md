# On-call brief — 2026-11-05

Answers come from project knowledge lookups. The evidence documents each answer rests on are listed under it.

## 1

**What does error code E4021 mean, and is it retryable?**

E4021 means **"Payment authorization expired"**: the authorization hold lapsed before capture. It is **not retryable**. To handle it, re-authorize and then capture. Do not retry the capture on its own. (Source: `lookup_error_code('E4021')`)

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "E4021 means 'Payment authorization expired'."},
  {"schema_version": 1, "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "The cause of E4021 is that the authorization hold lapsed before capture."},
  {"schema_version": 1, "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "The handling for E4021 is to re-authorize, then capture, and not to retry capture alone."},
  {"schema_version": 1, "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "E4021 is not retryable (Retryable: False)."}
]
```

## 2

**If PaymentsService is down, which services that call its API directly can no longer take payments?**

Two services call **PaymentsAPI** (which PaymentsService exposes) directly:

- **OrderService**
- **RenewalsWorker**

The service graph's direct-dependents lookup (1 hop) is complete and has no staleness caveats. Services that depend on PaymentsService only indirectly are not included. (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": [], "claim": "Within 1 hop of PaymentsService, the graph returns 2 affected services."},
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": [], "claim": "OrderService calls PaymentsAPI directly (CALLS edge), and PaymentsAPI is exposed by PaymentsService."},
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": [], "claim": "RenewalsWorker calls PaymentsAPI directly (CALLS edge), and PaymentsAPI is exposed by PaymentsService."}
]
```

## 3

**What are the NotificationsAPI retry semantics?**

This answer comes from the closest documents a vector search found (coverage: unknown), so it may not be the whole picture. The documents describe **NotificationsService**, not "NotificationsAPI" by name:

- It makes **3 attempts with a 250 ms backoff**. The `RETRY_ATTEMPTS` setting controls this.
- A message that fails all three attempts goes to the **dead-letter list**, and **the caller is not told**.
- Callers that need confirmation must **poll the message status**.

(Source: `search_docs('NotificationsAPI retry semantics', k=3)`)

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "NotificationsService retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "A message that fails all three attempts moves to the dead-letter list, and the caller is not told."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": [], "claim": "Callers that need confirmation poll the message status."}
]
```

## 4

**What was net written premium by region in Q3 2026?**

| Region | Net written premium, Q3 2026 |
|---|---:|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Definition (governed catalog, revision 2026-11-03): gross written premium minus cancellations, computed as `SUM(premium_amt) - SUM(cancellation_amt)` where `status != 'quote'`. Premium counts in the month it takes effect. Q3 covers `eff_dt` from 2026-07-01 up to but not including 2026-10-01. The source data does not state a currency. (Sources: `navigate_catalog`, `generate_governed_sql`, `execute_query`)

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 221, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "net_written_premium is gross written premium less cancellations, computed as SUM(premium_amt) - SUM(cancellation_amt) over rows where status != 'quote', recognized in the month the premium takes effect."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 100, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "The governed SQL restricts the Q3 2026 query to policies with eff_dt from 2026-07-01 up to but not including 2026-10-01."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "Q3 2026 net written premium for APAC is 278969.21."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "Q3 2026 net written premium for EMEA is 343269.84."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "Q3 2026 net written premium for LATAM is 308624.73."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "Q3 2026 net written premium for North America is 312420.42."}
]
```

## 5

**What was our loss ratio by region in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request because it does not model loss ratio, so it gives no number (`navigate_catalog(concept='loss ratio')`). A fallback document search found nothing relevant either. Its best match was a BillingService data-storage section, with low confidence and a score of 0.58 (`search_docs('loss ratio by region Q3 2026', k=3)`). No figure has been estimated here. The finance or actuarial team that owns this metric needs to provide it.

```json
[
  {"schema_version": 1, "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 53, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "No metric matches 'loss ratio', and the catalog does not model loss ratio. No number is stated for loss ratio by region in Q3 2026."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('loss ratio by region Q3 2026', k=3)"}, "confidence": "low", "coverage": "unknown", "cost_tokens": 211, "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"], "claim": "The vector search returned no section that reports loss ratio by region for Q3 2026; the top match was a BillingService data-storage section."}
]
```

## 6

**How much commission did we pay agents in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request because it does not model commission, so it gives no number (`navigate_catalog(concept='commission paid to agents')`). A fallback document search found nothing relevant either. Its best match was a PaymentsService operations section about provider retries, with low confidence and a score of 0.58 (`search_docs('commission paid to agents Q3 2026', k=3)`). No figure has been estimated here. The team that owns agent commissions needs to provide it.

```json
[
  {"schema_version": 1, "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 57, "freshness": "2026-11-05T16:49Z", "caveats": [], "claim": "No metric matches 'commission paid to agents', and the catalog does not model commission. No number is stated for commission paid to agents in Q3 2026."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('commission paid to agents Q3 2026', k=3)"}, "confidence": "low", "coverage": "unknown", "cost_tokens": 152, "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"], "claim": "The vector search returned no section that reports commission paid to agents for Q3 2026; the top match was a PaymentsService operations section about provider retries."}
]
```
