# On-call brief — 2026-11-05

Every answer comes from project knowledge. The evidence documents for each answer appear below it. Together the lookups cost 1,141 tokens, well under the 6,000 budget.

## 1

**E4021 means "Payment authorization expired". It is not retryable.** The authorization hold ran out before the payment was captured. To fix it, re-authorize and then capture. Don't retry the capture by itself. Source: `lookup_error_code('E4021')`.

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means 'Payment authorization expired': the authorization hold lapsed before capture; handling is re-authorize then capture (do not retry capture alone); Retryable: False.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 2

**OrderService and RenewalsWorker.** These are the two services that call PaymentsAPI directly. PaymentsAPI is exposed by PaymentsService, so both lose the ability to take payments if PaymentsService goes down. The search covered one hop (direct callers only) and is marked complete. Source: `find_dependents('PaymentsService', max_depth=1)`.

```json
[
  {"schema_version":1,"status":"found","claim":"Within 1 hop, OrderService and RenewalsWorker call PaymentsAPI (exposed by PaymentsService) directly and are affected if PaymentsService is down.","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]}
]
```

## 3

NotificationsAPI is exposed by NotificationsService.

- It makes **three attempts with a 250ms backoff**. The `RETRY_ATTEMPTS` setting controls this.
- A message that fails all three attempts goes to the **dead-letter list**. **The caller is not told.**
- Callers that need confirmation must poll the message status.

This answer comes from a document search (source: `search_docs('NotificationsAPI retry semantics', k=3)`, section `notifications-service#Delivery and retries`). A search can't confirm it found everything relevant, so this reflects the closest documents found.

```json
[
  {"schema_version":1,"status":"found","claim":"NotificationsService (which exposes NotificationsAPI) retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message failing all three moves to the dead-letter list without telling the caller, and callers needing confirmation poll message status.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 4

Net written premium for 2026-Q3 (policies taking effect July–September 2026), using catalog revision 2026-11-03:

| Region | Net written premium |
|---|---|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

The catalog defines this as premium minus cancellations, excluding quotes. Source: `execute_query(<signed SQL from generate_governed_sql>)`. The definition comes from `navigate_catalog(concept='net written premium')`.

```json
[
  {"schema_version":1,"status":"found","claim":"net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', month grain, with region as a valid dimension.","source":{"path":"semantic","identifier":"navigate_catalog(concept='net written premium', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":221,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Governed SQL was generated for net_written_premium by region over 2026-Q3 (eff_dt 2026-07-01 to before 2026-10-01).","source":{"path":"semantic","identifier":"generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":100,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium in 2026-Q3 by region: APAC 278969.21; EMEA 343269.84; LATAM 308624.73; North America 312420.42.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]}
]
```

## 5

**No answer: the governed catalog refused this.** The catalog doesn't model loss ratio, so there is no governed number to report (source: `navigate_catalog(concept='loss ratio')`). A follow-up document search found no relevant document either: the best match scored 0.60 and was low confidence (source: `search_docs('loss ratio by region', k=3)`). This brief doesn't calculate a loss ratio from other metrics, because no governed definition exists. Finance would need to supply a definition or a figure.

```json
[
  {"schema_version":1,"status":"refused","claim":"The governed catalog has no metric for 'loss ratio'; it explicitly does not model loss ratio.","source":{"path":"semantic","identifier":"navigate_catalog(concept='loss ratio', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":53,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The closest architecture documents for 'loss ratio by region' (BillingService data, ReportingService integrations, AuditService operations) do not describe loss ratio.","source":{"path":"vector","identifier":"search_docs('loss ratio by region', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":211,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```

## 6

**No answer: the governed catalog refused this.** No catalog metric matches agent commission. The metrics that can be queried are claims_paid, gross_written_premium, net_written_premium and policies_written (source: `navigate_catalog(concept='agent commission')`). A follow-up document search found nothing relevant: the best match scored 0.60 and was low confidence (source: `search_docs('agent commission paid', k=3)`). There is no number to report.

```json
[
  {"schema_version":1,"status":"refused","claim":"The governed catalog has no metric matching 'agent commission'; queryable metrics are claims_paid, gross_written_premium, net_written_premium, policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='agent commission', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":54,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The closest architecture documents for 'agent commission paid' (OrderService integrations, BillingService overview, PaymentsService operations) do not describe agent commission.","source":{"path":"vector","identifier":"search_docs('agent commission paid', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":160,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```
