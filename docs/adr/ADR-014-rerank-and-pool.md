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

## Result (EXP-009, WI-7) — Haiku stays; cross-encoder is a measured latency lever
Benchmarked Haiku vs a local cross-encoder (`ms-marco-MiniLM-L-6-v2`) on the same pool→top-5. **Identical
ranking quality** (both MRR 0.97, precision@1 0.94, recall@1/3/5 0.91/1.00/1.00) — no quality reason to
switch. The cross-encoder is ~26× faster (92 ms vs 2392 ms/query) and has zero API cost, but adds a
~2 GB PyTorch/sentence-transformers dependency to an otherwise all-API stack, and rerank latency is not
the bottleneck in a ~30–60 s agent loop. **Decision: keep Haiku for v1.** The cross-encoder is recorded
as a drop-in **scale/latency lever** (batch analysis, cost/latency pressure) — a one-line switch the day
it matters. See EXP-009.
