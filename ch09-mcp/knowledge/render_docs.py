#!/usr/bin/env python3
"""render_docs.py OUT_DIR: write the knowledge base as the Markdown files a
project would normally keep (docs/errors.md, docs/config-reference.md,
docs/architecture.md), for the file-access side of the Chapter 9 comparison."""
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
out.mkdir(parents=True, exist_ok=True)

codes = json.loads((here / "error_codes.json").read_text())
lines = ["# Error code reference", ""]
for e in codes.values():
    lines += [f"## {e['code']}: {e['title']}", "", f"- Cause: {e['cause']}",
              f"- Handling: {e['handling']}", f"- Retryable: {'yes' if e['retryable'] else 'no'}", ""]
(out / "errors.md").write_text("\n".join(lines))

schemas = json.loads((here / "config_schemas.json").read_text())
lines = ["# Service configuration reference", ""]
for service, keys in schemas.items():
    lines += [f"## {service}", "", "| Key | Type | Required | Default | Notes |", "|---|---|---|---|---|"]
    for key, m in keys.items():
        default = "secret" if m["secret"] else m["default"]
        lines.append(f"| `{key}` | {m['type']} | {'yes' if m['required'] else 'no'} | {default} | {m['description']} |")
    lines.append("")
(out / "config-reference.md").write_text("\n".join(lines))

arch = (here / "architecture.md").read_text()
(out / "architecture.md").write_text("# Architecture\n\n" + arch)
print(f"wrote {out}/errors.md, config-reference.md, architecture.md")
