# ADR-014: Reranker = Haiku; candidate pool = 10 → top_k = 5

Status: accepted
Date: 2026-06-24
Plan ref: ADR 3.4 · Evidence: EXP-001, EXP-003

## Context
The recall-first pool over-returns; a reranker re-scores it for true relevance. Choose the reranker
and the pool size feeding it.

## Options considered
- **Reranker:** Haiku LLM scorer vs dedicated cross-encoder vs none. "None" rejected by EXP-001 (naive
  hybrid MRR 0.79). Haiku measured: MRR 0.97, precision@1 0.95 — large, cheap (~$0.001/query) lift.
  Cross-encoder not yet benchmarked.
- **Pool size:** EXP-003 swept {3,5,8,16}. Small pools rank better un-reranked, but the reranker only
  sees the pool, so the pool must carry recall. pool=5 reaches recall@5 1.00; pool=10 adds headroom.

## Decision
**Haiku rerank, candidate pool = 10, final top_k = 5.** Dense-only fallback (no rerank) uses pool = 5.

## Why the others were rejected
None/naive-hybrid leaves precision on the table. A cross-encoder is a reasonable future comparison but
Haiku already reaches MRR 0.97 and reasons in-domain (it understands "running-account settlement"
phrasing). pool=10 buys recall insurance into the rerank stage — cheap protection against the project's
worst failure (a missed obligation) — and the reranker neutralises the extra noise.

## Consequences / what we'll measure
- Implemented as T5 (`tools/rerank.py`).
- Benchmark a cross-encoder reranker as a later EXP if precision plateaus.
- Watch rerank latency (one LLM round-trip); bound it in the agent loop (Phase 4).
