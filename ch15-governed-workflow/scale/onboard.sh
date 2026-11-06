#!/usr/bin/env bash
# Onboard a new team's service into a copy of the knowledge graph, without
# touching the execution side (skills, gate, plugin).
#
#   bash scale/onboard.sh            builds scale/build/ and prints each step
#   bash scale/onboard.sh --model    re-extracts the new document instead of
#                                    using the saved extraction (one model call)
#
# 1. copy Chapter 10's documents, saved extractions, and deployment manifest,
#    and build today's graph from them
# 2. add the new team's document (scale/docs/) and its line in the manifest
# 3. the manifest check fails: the graph doesn't know the new service yet
# 4. extract.py loads only the new document: from scale/extractions/, or with
#    --model from one model call
# 5. the manifest check passes
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
ch10=$here/../../ch10-graph
build=$here/build
rm -rf "$build" && mkdir -p "$build"
cp -r "$ch10/docs" "$build/docs"
cp -r "$ch10/graph/extractions" "$build/extractions"
cp "$ch10/deploy/services.txt" "$build/services.txt"
export GRAPH_DOCS=$build/docs GRAPH_CACHE=$build/extractions GRAPH_DB=$build/project-graph.db
python3 "$ch10/graph/extract.py" > /dev/null          # today's graph, from the saved extractions
cp "$here"/docs/*.md "$build/docs/"
echo LedgerService >> "$build/services.txt"
echo "== manifest check before extraction"
python3 "$ch10/eval/check_manifest.py" "$build/services.txt" "$GRAPH_DB" || true
echo "== loading the new document"
[ "${1:-}" = --model ] || cp "$here"/extractions/*.json "$build/extractions/"
python3 "$ch10/graph/extract.py" --model | tail -3
echo "== manifest check after extraction"
python3 "$ch10/eval/check_manifest.py" "$build/services.txt" "$GRAPH_DB"
