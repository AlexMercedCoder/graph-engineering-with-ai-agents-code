"""The Chapter 10 ontology: four entity types, four relationship types.

Lean by design. Extraction accuracy falls as the type count rises, so a type is
added only when a traversal that actually runs needs the distinction.
"""
ENTITY_TYPES = {"Service", "Database", "Configuration", "APIEndpoint"}
RELATIONSHIP_TYPES = {"CALLS", "STORES", "DEPENDS_ON", "CONFIGURES"}

EXTRACTION_PROMPT = """\
Read the document below and extract only entities and relationships that
match this schema. Do not infer relationships from proximity.

Entity types: Service, Database, Configuration, APIEndpoint
Relationship types: CALLS, STORES, DEPENDS_ON, CONFIGURES

For each relationship, quote the exact sentence that states it. If no
sentence states a relationship directly, do not emit it.

Return JSON matching the schema. Use no type outside the lists above.
"""

ALIASES = {
    "user service": "UserService",
    "users-api": "UsersAPI",
    "orders-api": "OrdersAPI",
    "notifications api": "NotificationsAPI",
    "payments api": "PaymentsAPI",
}
