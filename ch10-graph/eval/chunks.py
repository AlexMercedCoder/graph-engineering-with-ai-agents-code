"""The flat retriever the graph is measured against: one chunk per section, dense vectors.

Each chunk is a "## " section of a document, prefixed with the document title so
a chunk about "Data" still says whose data it is. Vectors come from fastembed's
BAAI/bge-small-en-v1.5 (pip install fastembed), and search is cosine similarity
over all chunks.
"""
import os
import re
from pathlib import Path

import numpy as np

DOCS = Path(os.environ.get("GRAPH_DOCS", Path(__file__).resolve().parent.parent / "docs"))
MODEL = "BAAI/bge-small-en-v1.5"
_index = None


def load_chunks():
    chunks = []
    for path in sorted(DOCS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.M).group(1).strip()
        for m in re.finditer(r"^##\s+(.+?)\n(.*?)(?=^##\s|\Z)", text, re.M | re.S):
            section, body = m.group(1).strip(), m.group(2).strip()
            chunks.append({"id": f"{path.stem}#{section}",
                           "text": f"{title}: {section}\n{body}"})
    return chunks


def _load():
    global _index
    if _index is None:
        from fastembed import TextEmbedding
        model = TextEmbedding(MODEL)
        chunks = load_chunks()
        vecs = np.array(list(model.embed([c["text"] for c in chunks])))
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
        _index = (model, chunks, vecs)
    return _index


def search(query, k=3):
    model, chunks, vecs = _load()
    q = np.array(list(model.query_embed([query]))[0])
    q /= np.linalg.norm(q)
    scores = vecs @ q
    order = np.argsort(-scores)[:k]
    return [dict(chunks[i], score=float(scores[i])) for i in order]


if __name__ == "__main__":
    import sys
    for hit in search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3):
        print(f"{hit['score']:.3f}  {hit['id']}")
