# On-call brief — 2026-11-05

Every answer below comes from the evidence documents included with it. Total retrieval cost: 1,141 tokens.

## 1

**What does E4021 mean, and is it retryable?**

E4021 means **Payment authorization expired**. The authorization hold ran out before the payment was captured. **It is not retryable.** Re-authorize first, then capture. Do not retry the capture on its own. Source: `lookup_error_code('E4021')`.

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means 'Payment authorization expired': the authorization hold lapsed before capture; handling is to re-authorize, then capture, and not retry capture alone; Retryable: False.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 2

**If PaymentsService is down, which services that call its API directly can no longer take payments?**

Two services call the PaymentsAPI (exposed by PaymentsService) directly:

- **OrderService** (OrderService -CALLS-> PaymentsAPI)
- **RenewalsWorker** (RenewalsWorker -CALLS-> PaymentsAPI)

Source: `find_dependents('PaymentsService', max_depth=1)`. Coverage is complete at 1 hop. Services that depend on these two indirectly are not listed here.

```json
[
  {"schema_version":1,"status":"found","claim":"Within 1 hop, OrderService and RenewalsWorker directly CALL the PaymentsAPI exposed by PaymentsService (2 affected).","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]}
]
```

## 3

**What are the NotificationsAPI retry semantics?**

NotificationsService exposes the NotificationsAPI. It makes **three attempts with a 250ms backoff**, set by `RETRY_ATTEMPTS`. If all three attempts fail, the message moves to the **dead-letter list and the caller is not told**. Callers that need confirmation must poll the message status. Source: `search_docs('NotificationsAPI retry semantics', k=3)` (section `notifications-service#Delivery and retries`).

Note: this comes from vector search, so coverage is unknown. It is the closest matching document, not a confirmed complete answer.

```json
[
  {"schema_version":1,"status":"found","claim":"NotificationsAPI (exposed by NotificationsService) retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message failing all three moves to the dead-letter list without telling the caller, and callers needing confirmation poll message status.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 4

**What was net written premium by region in Q3 2026?**

| Region | Net written premium (2026-Q3) |
|---|---:|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Definition: SUM(premium_amt) − SUM(cancellation_amt), counting rows where status ≠ 'quote', by policy effective date from 2026-07-01 up to 2026-10-01. The metric is owned by finance-reporting. Source: governed query, catalog revision 2026-11-03, signature 7fb718c0ff48a5b7. The catalog gives no currency.

```json
[
  {"schema_version":1,"status":"found","claim":"net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', at month grain, with region as a valid dimension; owner finance-reporting.","source":{"path":"semantic","identifier":"navigate_catalog(concept='net written premium', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":221,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Governed SQL was generated for net_written_premium by region over 2026-07-01 to 2026-10-01 (signature 7fb718c0ff48a5b7).","source":{"path":"semantic","identifier":"generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":100,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium in 2026-Q3 by region: APAC 278969.21, EMEA 343269.84, LATAM 308624.73, North America 312420.42.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]}
]
```

## 5

**What was our loss ratio by region in Q3 2026?**

**No answer is available, and no number is given.** The governed catalog refused the request because it does not model loss ratio. It does offer `claims_paid`, `gross_written_premium`, `net_written_premium` and `policies_written`. A follow-up search of the architecture documents found nothing relevant (low confidence, best match 0.60). Computing a loss ratio from other metrics would be an ungoverned figure, so none is shown. Ask finance-reporting for a governed loss-ratio source.

```json
[
  {"schema_version":1,"status":"refused","claim":"The catalog does not model loss ratio; queryable metrics are claims_paid, gross_written_premium, net_written_premium, policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='loss ratio', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":53,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The closest architecture documents for 'loss ratio by region' (billing-service#Data, reporting-service#Integrations, audit-service#Operations) do not mention loss ratio.","source":{"path":"vector","identifier":"search_docs('loss ratio by region', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":211,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```

## 6

**How much commission did we pay agents in Q3 2026?**

**No answer is available, and no number is given.** The governed catalog refused the request because no metric matches "agent commission". A follow-up search of the architecture documents found nothing relevant (low confidence, best match 0.60). A governed commission metric would need to be added before this can be answered.

```json
[
  {"schema_version":1,"status":"refused","claim":"No catalog metric matches 'agent commission'; queryable metrics are claims_paid, gross_written_premium, net_written_premium, policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='agent commission', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":54,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The closest architecture documents for 'agent commission paid' (order-service#Integrations, billing-service#Overview, payments-service#Operations) do not mention agent commission.","source":{"path":"vector","identifier":"search_docs('agent commission paid', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":160,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```
