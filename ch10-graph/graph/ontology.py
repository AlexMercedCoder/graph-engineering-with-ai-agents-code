"""The Chapter 10 ontology: four entity types, five relationship types.

Lean by design. Extraction accuracy falls as the type count rises, so a type is
added only when a traversal that actually runs needs the distinction.
"""
ENTITY_TYPES = {"Service", "Database", "Configuration", "APIEndpoint"}
RELATIONSHIP_TYPES = {"CALLS", "EXPOSES", "STORES", "DEPENDS_ON", "CONFIGURES"}

# Which entity types each relationship may connect, source first. validate()
# rejects an edge that breaks its signature, which also catches reversed edges.
SIGNATURES = {
    "CALLS": ("Service", "APIEndpoint"),
    "EXPOSES": ("Service", "APIEndpoint"),
    "STORES": ("Service", "Database"),
    "DEPENDS_ON": ("Service", "Service"),
    "CONFIGURES": ("Configuration", "Service"),
}

EXTRACTION_PROMPT = """\
Read the document below and extract only entities and relationships that
match this schema. Do not infer relationships from proximity.

Entity types: Service, Database, Configuration, APIEndpoint
Relationship types:
  CALLS       Service -> APIEndpoint
  EXPOSES     Service -> APIEndpoint
  STORES      Service -> Database
  DEPENDS_ON  Service -> Service
  CONFIGURES  Configuration -> Service

For each relationship, quote the exact sentence that states it. If no
sentence states a relationship directly, do not emit it.

Return only JSON in this shape, with no type outside the lists above:
{"entities": [{"name": "...", "type": "..."}],
 "relationships": [{"source": "...", "type": "...", "target": "...",
                    "sentence": "..."}]}
"""

# Grows from review: after an extraction run, list the distinct node names
# (python3 extract.py --names), read down the list, and add each duplicate here.
ALIASES = {
    "gateway": "ApiGateway",
    "orders": "OrdersPostgresDatabase",
    "payments": "PaymentsPostgresDatabase",
    "users": "UsersPostgresDatabase",
}
