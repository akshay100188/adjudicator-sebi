# ADR-011: Retrieval architecture — hybrid candidate generation + rerank

Status: accepted
Date: 2026-06-24
Plan ref: ADR 3.1 · Evidence: EXP-001

## Context
Choose the retrieval stack that feeds the agent: pure-dense, pure-sparse, hybrid, or hybrid+rerank.
Recall-first (a missed obligation is the worst failure).

## Options considered (measured, EXP-001 on 20 golden queries)
- **Pure-dense** — MRR 0.90, recall@5 1.00, ~1.8s, no LLM. Strong + cheap; blurs exact tokens.
- **Pure-sparse (native FTS)** — MRR 0.61, recall@5 0.93. Catches exact terms; noisy ranking.
- **Naive hybrid (RRF)** — MRR 0.79. *Worse* than dense here: fusion dilutes a strong dense signal
  with sparse noise on a small, semantically-separable corpus.
- **Hybrid + Haiku rerank** — MRR 0.97, recall@3 1.00, precision@1 0.95. Best, but +Haiku cost/latency.

## Decision
**Hybrid for recall-first candidate generation, then Haiku rerank for final ordering.** The hybrid
pool guarantees the right obligation is retrieved (incl. exact-term queries dense misses); the
reranker supplies precision.

## Why the others were rejected
Pure-sparse ranks poorly. Naive hybrid measurably *underperforms* dense on this corpus — fusion is
not free. Pure-dense is the strong, cheap fallback we keep documented, but it leaves exact-term recall
and corpus-growth robustness on the table. Rerank is what turns the recall-first pool into a precise
result, and the lift is large (MRR 0.79→0.97).

## Consequences / what we'll measure
- The agent's T2 (hybrid) + T5 (rerank) tools implement this.
- Re-benchmark dense-vs-hybrid and the embedding model (ADR-004) once more chapters are ingested —
  hybrid's exact-term value should grow as the corpus does.
- Cost: rerank adds ~$0.001/query (Haiku) + ~one round-trip latency.
