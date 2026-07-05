# Post-rerank recall eval — 2026-07-04

Config: hybrid pool=10, RRF k=60, Haiku rerank -> top-5. 35 golden queries. Same tools the agent calls (ADR-014).

Guards the recall the agent **actually consumes** (reranked top-5), which the deterministic CI gate (raw pool recall) never measures. See ADR-019.

## Recall: raw hybrid pool vs. reranked top-k

| metric | raw-hybrid pool | post-rerank | delta |
|---|---|---|---|
| recall@1 | 0.60 | 0.91 | +0.31 |
| recall@3 | 0.84 | 1.00 | +0.16 |
| recall@5 | 0.99 | 1.00 | +0.01 |

## Rerank drops (gold in raw pool, absent from reranked top-5)

**None.** The reranker did not drop a single gold obligation that the raw pool retrieved — it is faithful: it reorders for precision without costing recall.

