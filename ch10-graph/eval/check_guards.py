#!/usr/bin/env python3
"""Feed extract_document() a model reply with one of each extraction error.

The reply below is written by hand: an edge whose quote is paraphrased, an
edge with an invented relationship type, a CONFIGURES edge pointing the wrong
way, and a duplicate name that the alias table should fold. Every guard should
fire, and only the one correct edge should survive.
"""
import sys
from pathlib import Path

GRAPH = Path(__file__).resolve().parent.parent / "graph"
sys.path.insert(0, str(GRAPH))
from extract import extract_document

reply = {
    "entities": [
        {"name": "PaymentsService", "type": "Service"},
        {"name": "BillingService", "type": "Service"},
        {"name": "NotificationsAPI", "type": "APIEndpoint"},
        {"name": "payments", "type": "Database"},
        {"name": "PAYMENT_API_KEY", "type": "Configuration"},
    ],
    "relationships": [
        {"source": "PaymentsService", "type": "CALLS", "target": "NotificationsAPI",
         "sentence": "It calls the NotificationsAPI on a declined authorization, so the customer "
                     "hears about a decline even when checkout has already returned."},
        {"source": "PaymentsService", "type": "DEPENDS_ON", "target": "BillingService",
         "sentence": "PaymentsService works closely with BillingService."},
        {"source": "PaymentsService", "type": "MAINTAINED_WITH", "target": "BillingService",
         "sentence": "PaymentsService is maintained by the same team as BillingService."},
        {"source": "PaymentsService", "type": "CONFIGURES", "target": "PAYMENT_API_KEY",
         "sentence": "It is configured by PAYMENT_API_KEY and CAPTURE_TIMEOUT."},
        {"source": "PaymentsService", "type": "STORES", "target": "payments",
         "sentence": "It stores authorizations in the payments Postgres database, with the "
                     "provider's reference for each one."},
    ],
}
log = []
res = extract_document(GRAPH.parent / "docs" / "payments-service.md", reply, log)
for line in log:
    print(line)
for e in res["edges"]:
    print(f"kept:    {e['source']} -{e['type']}-> {e['target']}")
ok = [(e["type"], e["target"]) for e in res["edges"]] == [
    ("CALLS", "NotificationsAPI"), ("STORES", "PaymentsPostgresDatabase")] and len(log) == 3
print("all guards fired" if ok else "UNEXPECTED RESULT")
sys.exit(0 if ok else 1)
