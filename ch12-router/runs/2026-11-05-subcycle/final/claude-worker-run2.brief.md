# On-call brief — 2026-11-05

## 1

**What does error code E4021 mean, and is it retryable?**

E4021 means **"Payment authorization expired"**: the authorization hold lapsed before capture. It is **not retryable**. To handle it, re-authorize and then capture. Retrying the capture on its own won't work. (Source: `lookup_error_code('E4021')`)

```json
[
  {"schema_version": 1, "claim": "E4021 means 'Payment authorization expired'.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "The cause of E4021 is that the authorization hold lapsed before capture.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "E4021 is not retryable (Retryable: False); its handling is to re-authorize, then capture, and not to retry capture alone.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []}
]
```

## 2

**If PaymentsService is down, which services that call its API directly can no longer take payments?**

Two services call PaymentsAPI (exposed by PaymentsService) directly:

- **OrderService**
- **RenewalsWorker**

Caveat: the service graph only records CALLS edges. It doesn't say how these services behave when PaymentsService is down, for example whether they queue or fall back. These are the direct callers that depend on it, but the graph doesn't confirm that they can't take payments during an outage. The query covered direct callers only (max_depth=1). (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {"schema_version": 1, "claim": "OrderService calls PaymentsAPI, which is exposed by PaymentsService, so it is a direct caller of PaymentsService.", "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": ["Graph lists CALLS edges only; it does not state how OrderService behaves when PaymentsService is down.", "Query run with max_depth=1, so only direct callers are listed."]},
  {"schema_version": 1, "claim": "RenewalsWorker calls PaymentsAPI, which is exposed by PaymentsService, so it is a direct caller of PaymentsService.", "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": ["Graph lists CALLS edges only; it does not state how RenewalsWorker behaves when PaymentsService is down.", "Query run with max_depth=1, so only direct callers are listed."]}
]
```

## 3

**What are the NotificationsAPI retry semantics?**

- NotificationsAPI makes **3 attempts with a 250 ms backoff**, set by `RETRY_ATTEMPTS`.
- If all three attempts fail, the message moves to the **dead-letter list** and **the caller is not told**.
- Callers that need confirmation have to **poll the message status**.

Note: this comes from a document search (coverage unknown). It reflects the closest documents found, not a guaranteed complete spec. (Source: `search_docs('NotificationsAPI retry semantics', k=3)`)

```json
[
  {"schema_version": 1, "claim": "NotificationsAPI retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS.", "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "A NotificationsAPI message that fails all three attempts moves to the dead-letter list, and the caller is not told.", "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "Callers of NotificationsAPI that need confirmation poll the message status.", "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 222, "freshness": "2026-11-04T02:09Z", "caveats": []}
]
```

## 4

**What was net written premium by region in Q3 2026?**

| Region        | Net written premium, Q3 2026 |
|---------------|-----------------------------:|
| APAC          | 278,969.21 |
| EMEA          | 343,269.84 |
| LATAM         | 308,624.73 |
| North America | 312,420.42 |

Definition: `SUM(premium_amt) - SUM(cancellation_amt)` over rows where status != 'quote', counted in the month the premium takes effect. Scope: effective dates 2026-07-01 to 2026-09-30, grouped by region via `analytics.dim_geography`. (Sources: `navigate_catalog(concept='net written premium')`; `execute_query(<signed SQL from generate_governed_sql>)`, catalog revision 2026-11-03)

```json
[
  {"schema_version": 1, "claim": "net_written_premium is computed as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', recognized in the month the premium takes effect.", "status": "found", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 221, "freshness": "2026-11-05T16:49Z", "caveats": []},
  {"schema_version": 1, "claim": "Net written premium for APAC in 2026-Q3 is 278969.21.", "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": ["Scope: policies with status != 'quote' and effective date 2026-07-01 to 2026-09-30, grouped by region via analytics.dim_geography."]},
  {"schema_version": 1, "claim": "Net written premium for EMEA in 2026-Q3 is 343269.84.", "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": ["Scope: policies with status != 'quote' and effective date 2026-07-01 to 2026-09-30, grouped by region via analytics.dim_geography."]},
  {"schema_version": 1, "claim": "Net written premium for LATAM in 2026-Q3 is 308624.73.", "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": ["Scope: policies with status != 'quote' and effective date 2026-07-01 to 2026-09-30, grouped by region via analytics.dim_geography."]},
  {"schema_version": 1, "claim": "Net written premium for North America in 2026-Q3 is 312420.42.", "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-05T16:49Z", "caveats": ["Scope: policies with status != 'quote' and effective date 2026-07-01 to 2026-09-30, grouped by region via analytics.dim_geography."]}
]
```

## 5

**What was our loss ratio by region in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request because it doesn't model loss ratio. The queryable metrics are claims_paid, gross_written_premium, net_written_premium and policies_written. A fallback document search found nothing relevant. Its closest match (billing-service#Data, score 0.58, low confidence) is about invoice numbering. No figure is given here; for an official number, ask the data/finance owners. (Sources: `navigate_catalog(concept='loss ratio')`; `search_docs('loss ratio by region Q3 2026', k=3)`)

```json
[
  {"schema_version": 1, "claim": "The catalog does not model loss ratio.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 53, "freshness": "2026-11-05T16:49Z", "caveats": ["The catalog lists claims_paid, gross_written_premium, net_written_premium, and policies_written as queryable; none is a loss ratio. No number is stated."]},
  {"schema_version": 1, "claim": "The top match for 'loss ratio by region Q3 2026' (billing-service#Data, score 0.58) describes invoice numbering and does not define a loss ratio.", "status": "found", "source": {"path": "vector", "identifier": "search_docs('loss ratio by region Q3 2026', k=3)"}, "confidence": "low", "coverage": "unknown", "cost_tokens": 211, "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"]}
]
```

## 6

**How much commission did we pay agents in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request because it doesn't model agent commission. A fallback document search found nothing relevant. Its closest match (payments-service#Operations, score 0.58, low confidence) is about provider call retries. No figure is given here; ask the finance owners. (Sources: `navigate_catalog(concept='commission paid to agents')`; `search_docs('commission paid to agents Q3 2026', k=3)`)

```json
[
  {"schema_version": 1, "claim": "The catalog does not model commission paid to agents.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 57, "freshness": "2026-11-05T16:49Z", "caveats": ["The catalog lists claims_paid, gross_written_premium, net_written_premium, and policies_written as queryable; none is a commission metric. No number is stated."]},
  {"schema_version": 1, "claim": "The top match for 'commission paid to agents Q3 2026' (payments-service#Operations, score 0.58) describes provider call retries and does not mention agent commissions.", "status": "found", "source": {"path": "vector", "identifier": "search_docs('commission paid to agents Q3 2026', k=3)"}, "confidence": "low", "coverage": "unknown", "cost_tokens": 152, "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"]}
]
```
