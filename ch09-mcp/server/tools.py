"""The three Chapter 9 tools, as plain functions.

server.py wraps these for MCP. cli.py wraps the same functions for a shell, which
is the substitute the chapter describes for a harness without MCP. One
implementation, two surfaces, so the two cannot drift apart.
"""
from knowledge import (
    ERROR_CODES, KNOWN_SERVICES, TOPICS,
    current_identity, render_schema, search_sections, suggest_nearby,
    visible_classifications,
)


def lookup_error_code(code: str) -> str:
    """Return the meaning, cause, and recommended handling for a project error
    code. Use when an error code appears in logs, a stack trace, or an API
    response. Codes match the pattern E followed by four digits."""
    entry = ERROR_CODES.get((code or "").upper())
    if entry is None:
        near = suggest_nearby(code)
        return f"No error code {code}. Nearest known codes: {', '.join(near)}."
    return (
        f"{entry['code']}: {entry['title']}\n"
        f"Cause: {entry['cause']}\n"
        f"Handling: {entry['handling']}\n"
        f"Retryable: {entry['retryable']}"
    )


def get_config_schema(service: str) -> str:
    """Return the configuration schema for one named service: keys, types,
    defaults, and which keys are required. Use before generating or editing a
    service configuration file. Returns the schema only, never the values from
    any environment."""
    from knowledge import SCHEMAS
    if service not in KNOWN_SERVICES:
        return f"Unknown service {service}. Known services: {', '.join(KNOWN_SERVICES)}."
    return render_schema(SCHEMAS[service])


def find_architecture_docs(topic: str, max_sections: int = 3) -> str:
    """Search the project architecture documentation and return the matching
    sections, up to max_sections. Use when a question concerns how services
    relate, why a design decision was made, or where a responsibility lives.
    Returns sections, not whole documents."""
    identity = current_identity()
    allowed = visible_classifications(identity)
    hits = [h for h in search_sections(topic) if h["classification"] in allowed]
    hits = hits[:max(1, min(max_sections, 5))]
    if not hits:
        # Same answer shape for absent and forbidden, so the failure does not leak.
        return f"No architecture sections match {topic!r}. Available topics: {', '.join(TOPICS[:4])}."
    return "\n\n".join(f"## {h['title']}\n{h['body']}" for h in hits)
