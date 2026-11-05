# One-shot retrieval

`chunks.py` over the 41 sections of `docs/` (fastembed 0.9.1, `BAAI/bge-small-en-v1.5`).
`recall.txt` is `recall.py -v`: for each question, the share of its supporting sections in the top k.

| k | Single-hop, all sections returned | Multi-hop, all sections returned | Multi-hop, mean share |
|---|---|---|---|
| 3 | 10/10 | 1/10 | 43% |
| 5 | 10/10 | 3/10 | 59% |

`multi-hop-top5.txt` and `single-hop-top3.txt` are the two queries the chapter shows.
