# Chapter 15: Shipping the Governed Workflow

The snippets from Chapter 15. The chapter assembles the components from the
other directories into a governed workflow and adds the human approval gate
that sits in front of any tool call whose impact is hard to reverse.

## The approval packet

Chapter 15 shows how a hook builds an approval packet that names the operation,
the evidence, the blast radius, and the fallbacks. This is the shape of the
packet, shown as a structured request for a destructive migration.

```text
OPERATION
  Apply migration 0042_add_policy_index to production.

WHY
  Query p95 on policy lookup is 3.2s against a 500ms target.
  Evidence: catalog:query-plan:2026-08-11T09:14Z (confidence 0.91, coverage complete)

AFFECTS
  fct_policy_premium (48M rows), and 3 downstream services:
  BillingService, ReportingService, RenewalsWorker
  Source: graph:traversal:fct_policy_premium (coverage complete)

REVERSIBLE
  Index creation: yes, by dropping the index.
  Table lock during creation: no. Estimated 40 to 90 seconds.

ALTERNATIVES
  1. Apply during the Sunday maintenance window (no user impact, 4 day delay).
  2. Create the index concurrently (no lock, roughly 6x slower, more disk).
  3. Do nothing. The p95 target continues to be missed.
```

## The hook that demands approval

The hook raises the permission decision to `ask` whenever a tool call is not
already reversible. The decision packet carries the evidence assembled from the
graph. This is the `PreToolUse` pattern from Chapter 6, wired to the governance
policy from this chapter.

```python
if requires_approval(tool_name, tool_input):
    packet = build_approval_packet(tool_name, tool_input, evidence)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": packet,
        }
    }))
    sys.exit(0)
```

The deployment checklist that orchestrates these decisions lives in the
chapter. The components it assembles are in the other directories: the router
in `ch12-router/`, the trace pipeline in `ch14-observability/`, and the plugin
packaging in `ch07-plugin/`.
