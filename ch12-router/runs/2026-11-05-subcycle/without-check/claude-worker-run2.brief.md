# On-call brief (2026-11-05)

## 1

**What E4021 means:** **E4021 means "Payment authorization expired."** The authorization hold ran out before the payment was captured.

**Is it retryable?** **No.** To handle it, re-authorize the payment and then capture it. Do not retry the capture on its own.

Source: `lookup_error_code('E4021')`. Confidence high, coverage complete.

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 is the code for 'Payment authorization expired'.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"E4021 is caused by the authorization hold lapsing before capture.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The handling for E4021 is to re-authorize, then capture, and not to retry capture alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"E4021 is not retryable (Retryable: False).","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 2

**Two services call PaymentsService's API (PaymentsAPI) directly: OrderService and RenewalsWorker.** If PaymentsService is down, both lose the ability to take payments. This list covers direct callers only (one hop). Services that reach PaymentsService through another service are not included.

Source: `find_dependents('PaymentsService', max_depth=1)`. Confidence high, coverage complete, no staleness caveats.

```json
[
  {"schema_version":1,"status":"found","claim":"Within one hop, OrderService calls PaymentsAPI directly, and PaymentsAPI is exposed by PaymentsService.","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Within one hop, RenewalsWorker calls PaymentsAPI directly, and PaymentsAPI is exposed by PaymentsService.","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The graph reports 2 direct callers of PaymentsService's API within 1 hop: OrderService and RenewalsWorker.","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]}
]
```

## 3

This answer comes from the closest documents a vector search found (coverage: unknown), so it may not be complete. The documents describe **NotificationsService**, not "NotificationsAPI" by name.

- **Retries:** delivery is tried **3 times in total**, with a **250 ms backoff**. The count is set by `RETRY_ATTEMPTS`.
- **After all attempts fail:** the message goes to the **dead-letter list**. **The caller is not told.**
- **Confirming delivery:** callers that need confirmation must **poll the message status**.

Source: `search_docs('NotificationsAPI retry semantics', k=3)`.

```json
[
  {"schema_version":1,"status":"found","claim":"NotificationsService retries message delivery three attempts in total, with a 250ms backoff, configured by RETRY_ATTEMPTS.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"A message that fails all three attempts moves to the dead-letter list, and the caller is not told.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Callers that need delivery confirmation poll the message status.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 4

Net written premium by region for 2026-Q3 (effective dates 2026-07-01 up to, not including, 2026-10-01). Figures come from governed SQL run against catalog revision 2026-11-03.

| Region        | Net written premium |
|---------------|--------------------:|
| APAC          | 278,969.21 |
| EMEA          | 343,269.84 |
| LATAM         | 308,624.73 |
| North America | 312,420.42 |

The catalog defines this metric as gross written premium minus cancellations: `SUM(premium_amt) - SUM(cancellation_amt)`, excluding quotes. The finance-reporting team owns the definition. The evidence does not give a currency.

Sources: `navigate_catalog(concept='net written premium')`, `generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)`, `execute_query(<signed SQL>)`.

```json
[
  {"schema_version":1,"status":"found","claim":"The catalog defines net_written_premium as gross written premium less cancellations, computed as SUM(premium_amt) - SUM(cancellation_amt), counting rows where status != 'quote', owned by finance-reporting.","source":{"path":"semantic","identifier":"navigate_catalog(concept='net written premium', entity='')","revision":null},"confidence":"high","coverage":"complete","cost_tokens":221,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The governed SQL computes net_written_premium by region from analytics.fct_policy_premium joined to analytics.dim_geography, filtering status != 'quote' and eff_dt from 2026-07-01 up to but not including 2026-10-01.","source":{"path":"semantic","identifier":"generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":100,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 in APAC was 278969.21.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 in EMEA was 343269.84.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 in LATAM was 308624.73.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 in North America was 312420.42.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]}
]
```

## 5

**No answer is available.** The governed catalog **refused** this question because it does not model loss ratio. It can only query claims_paid, gross_written_premium, net_written_premium and policies_written. A fallback vector search found no document with a loss ratio value; the best match scored only 0.58.

No loss ratio figure is given here. Working one out from claims_paid and premium would mean choosing a definition the catalog doesn't govern. If that's needed, finance-reporting should define it.

```json
[
  {"schema_version":1,"status":"refused","claim":"The catalog does not model loss ratio. Metrics it can query are claims_paid, gross_written_premium, net_written_premium, and policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='loss ratio', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":53,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"None of the top 3 vector results for loss ratio by region in Q3 2026 states a loss ratio value; they cover BillingService invoice numbering, ReportingService dependencies, and AuditService flush retries.","source":{"path":"vector","identifier":"search_docs('loss ratio by region Q3 2026', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":211,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.58; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```

## 6

**No answer is available.** The governed catalog **refused** this question because no catalog metric covers commission paid to agents. A fallback vector search found no document with a commission amount; the best match scored only 0.57. No figure is given here.

```json
[
  {"schema_version":1,"status":"refused","claim":"No catalog metric matches commission paid to agents. Metrics it can query are claims_paid, gross_written_premium, net_written_premium, and policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='commission paid to agents', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":57,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"None of the top 3 vector results for agent commission paid in Q3 2026 states a commission amount; they describe PaymentsService network-error retries, RenewalsWorker renewal retries, and OrderService timeout handling.","source":{"path":"vector","identifier":"search_docs('agent commission paid Q3 2026', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":173,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.57; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```
