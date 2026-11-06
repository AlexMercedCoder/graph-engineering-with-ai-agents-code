#!/usr/bin/env bash
# Assemble the Chapter 11 server into an MCP Bundle and pack it.
#
#   bash bundle/build.sh        # writes bundle/governed-data-local.mcpb
#
# Needs Node.js (for npx) and network access the first time, to fetch the
# @anthropic-ai/mcpb command line. The bundle carries the warehouse and its
# policies, which is the reason Chapter 13 doesn't give it to analysts.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
ch11="$here/../../ch11-catalog"
[ -f "$ch11/warehouse/warehouse.db" ] || python3 "$ch11/warehouse/seed.py" > /dev/null
build="$here/build/governed-data-local"
rm -rf "$here/build" && mkdir -p "$build/server" "$build/warehouse"
cp "$here/manifest.json" "$here/pyproject.toml" "$build/"
cp "$ch11/server/server.py" "$ch11/server/tools.py" "$build/server/"
cp "$ch11/validate.py" "$ch11/catalog.yaml" "$build/"
cp "$ch11/warehouse/dataplatform.py" "$ch11/warehouse/policies.yaml" "$ch11/warehouse/warehouse.db" "$build/warehouse/"
npx -y @anthropic-ai/mcpb@2.1.2 validate "$build/manifest.json"
npx -y @anthropic-ai/mcpb@2.1.2 pack "$build" "$here/governed-data-local.mcpb"
