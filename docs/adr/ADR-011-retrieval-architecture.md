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

## Status note (Phase 7)
To keep the interview narrative honest: on the current 54-obligation corpus, **rerank supplies the
precision lift, not hybrid.** The measured picture (EXP-001, EXP-004) is:
- **Rerank is the decisive component:** it lifts MRR 0.79 → 0.97 and recall@1 0.60 → 0.91
  (post-rerank recall eval, WI-1 / ADR-019). That is where the quality comes from.
- **Hybrid vs. pure-dense is a wash-to-slight-loss pre-rerank:** naive hybrid (MRR 0.79/0.74) actually
  *underperforms* pure-dense (MRR 0.90/0.86) at 16 and 54 obligations, because RRF dilutes a strong
  dense signal with noisier sparse ranks on a small, semantically-separable corpus (EXP-001 finding 3,
  EXP-004 finding 3). The classic BM25 exact-term win does not even apply here: chunks are paraphrased
  and carry no circular-number tokens to match on (ADR-013).
- **Hybrid is therefore kept as an *insurance bet*, not a measured current-corpus win** — insurance for
  (a) corpus growth (sparse exact-term value should appear as dense degrades on a larger, denser corpus)
  and (b) exact-term robustness. Re-benchmark dense-vs-hybrid per the ADR-011 re-benchmark trigger as
  chapters are added. Do **not** claim "hybrid helped" on today's numbers — it did not; rerank did.
