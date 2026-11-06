# On-call brief — 2026-11-05

Answers come from project knowledge lookups. Each section lists the evidence documents it rests on.

## 1

**E4021 = "Payment authorization expired."** The authorization hold lapsed before capture. **It is not retryable.** To handle it, re-authorize and then capture. Do not retry the capture by itself. (Source: `lookup_error_code('E4021')`)

```json
[
  {"schema_version": 1, "status": "found", "claim": "Error code E4021 is named 'Payment authorization expired'.", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "E4021 is caused by the authorization hold lapsing before capture.", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "E4021 is not retryable (Retryable: False).", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "The handling for E4021 is to re-authorize, then capture, and not to retry capture alone.", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:09Z", "caveats": []}
]
```

## 2

**OrderService and RenewalsWorker.** These are the only two services the service graph shows calling PaymentsAPI (which PaymentsService exposes) directly, one hop away. This does not include services further upstream that depend on payments only through these two. (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {"schema_version": 1, "status": "found", "claim": "OrderService calls PaymentsAPI directly, and PaymentsAPI is exposed by PaymentsService.", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:56Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "RenewalsWorker calls PaymentsAPI directly, and PaymentsAPI is exposed by PaymentsService.", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:56Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "Within one hop, the service graph reports exactly two direct callers of PaymentsService: OrderService and RenewalsWorker.", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-04T02:56Z", "caveats": []}
]
```

## 3

This answer comes from the closest architecture documents a document search found (coverage: unknown), so the docs may not cover everything. The matching docs describe this behavior under the name **NotificationsService**:

- A failed delivery gets **3 attempts in total**, with a **250 ms backoff**. The attempt count is set by `RETRY_ATTEMPTS`.
- If all attempts fail, the message goes to the **dead-letter list**. **The calling service is not told.**
- Callers that need delivery confirmation **must poll the message status**.

(Source: `search_docs('NotificationsAPI retry semantics', k=3)`)

```json
[
  {"schema_version": 1, "status": "found", "claim": "NotificationsService retries a failed delivery three attempts in total, with a 250ms backoff, and the attempt count is configured by RETRY_ATTEMPTS.", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "A message that fails all three attempts moves to the dead-letter list, and the calling service is not told.", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "Callers that need delivery confirmation must poll the message status.", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"}, "confidence": "high", "coverage": "unknown", "freshness": "2026-11-04T02:09Z", "caveats": []}
]
```

## 4

Net written premium, Q3 2026 (from the governed catalog, revision 2026-11-03):

| Region | Net written premium |
|---|---:|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

How it is defined: SUM(premium_amt) − SUM(cancellation_amt), excluding rows with status `quote`, for policies with eff_dt from 2026-07-01 up to but not including 2026-10-01. (Sources: `navigate_catalog(concept='net written premium')`, `generate_governed_sql(...)`, `execute_query(...)`)

```json
[
  {"schema_version": 1, "status": "found", "claim": "Net written premium is gross written premium less cancellations, computed as SUM(premium_amt) - SUM(cancellation_amt) over rows where status is not 'quote', recognized in the month the premium takes effect.", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-05T16:49Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "The governed query for 2026-Q3 covers policies with eff_dt from 2026-07-01 up to but not including 2026-10-01, excludes status 'quote', and is grouped by region.", "source": {"path": "semantic", "identifier": "generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-05T16:49Z", "caveats": []},
  {"schema_version": 1, "status": "found", "claim": "Q3 2026 net written premium by region was APAC 278969.21, EMEA 343269.84, LATAM 308624.73, and North America 312420.42 (4 rows).", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-05T16:49Z", "caveats": []}
]
```

## 5

**No answer available.** The governed catalog **refused** this question because it does not model loss ratio. The only metrics it can query are claims_paid, gross_written_premium, net_written_premium and policies_written. A follow-up document search found nothing relevant either (low confidence; the best match scored 0.60 and was about BillingService invoice numbering). No figure is given here, and none was calculated from other metrics, because the governed definition of loss ratio is not available. The data/finance owner needs to supply it.

```json
[
  {"schema_version": 1, "status": "refused", "claim": "The governed catalog refuses 'loss ratio' because it does not model loss ratio; the queryable metrics are claims_paid, gross_written_premium, net_written_premium, and policies_written. No loss ratio number is stated.", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-05T16:49Z", "caveats": ["re-routed to vector after semantic returned refused"]},
  {"schema_version": 1, "status": "found", "claim": "The architecture documents contain no section defining or reporting loss ratio by region; the top match (score 0.60) describes BillingService invoice numbering. No loss ratio figure is available from either path.", "source": {"path": "vector", "identifier": "search_docs('loss ratio by region', k=3)"}, "confidence": "low", "coverage": "unknown", "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.60; the documents may not cover this", "re-routed to vector after semantic returned refused"]}
]
```

## 6

**No answer available.** The governed catalog **refused** this question because it does not model commission paid to agents. A follow-up document search found nothing relevant (low confidence; the top matches scored 0.61 and covered PaymentsService retries, OrderService integrations and the BillingService overview). No figure is given here. This needs a source outside project knowledge, such as finance or the agent-compensation system.

```json
[
  {"schema_version": 1, "status": "refused", "claim": "The governed catalog refuses 'commission paid to agents' because it does not model that concept; the queryable metrics are claims_paid, gross_written_premium, net_written_premium, and policies_written. No commission number is stated.", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"}, "confidence": "high", "coverage": "complete", "freshness": "2026-11-05T16:49Z", "caveats": ["re-routed to vector after semantic returned refused"]},
  {"schema_version": 1, "status": "found", "claim": "The architecture documents contain no section reporting commissions paid to agents; the top three matches (scores 0.61) cover PaymentsService retries, OrderService integrations, and the BillingService overview. No commission figure is available from either path.", "source": {"path": "vector", "identifier": "search_docs('commission paid to agents', k=3)"}, "confidence": "low", "coverage": "unknown", "freshness": "2026-11-04T02:09Z", "caveats": ["best match scored 0.61; the documents may not cover this", "re-routed to vector after semantic returned refused"]}
]
```
