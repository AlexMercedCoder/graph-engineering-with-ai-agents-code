# LadybugDB

`python3 graph/ladybug_graph.py` with ladybug 0.22.1 (released 2026-10-28; LadybugDB is the
community fork of Kuzu): loads the SQLite graph (27 nodes, 30 edges) into an embedded LadybugDB
database and runs the Cypher form of `find_dependents NotificationsAPI 2`. `output.txt` lists
BillingService and PaymentsService at one hop and OrderService, RenewalsWorker, and ReportingService
at two, the same five services `graph/query.py dependents NotificationsAPI 2` returns.
