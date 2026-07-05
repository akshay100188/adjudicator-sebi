# ADR-004: Embedding model for v1

Status: accepted
Date: 2026-06-23
Decision ref: §10 Decision D / plan ADR 3.1

## Context
Dense retrieval needs an embedding model. The plan flags this as worth benchmarking (Voyage / Cohere
/ BGE vs. OpenAI), but a benchmark needs the retrieval substrate and golden query set to exist first.

## Options considered
- **Keep `text-embedding-3-small` @ 512 dims now; benchmark later** — Pro: unblocks Phases 1–3
  immediately; cheap storage (512 not 1536); a known-good baseline. Con: may leave recall on the
  table vs. a domain-stronger model.
- **Benchmark Voyage / Cohere / BGE up front** — Pro: pick the best embedder before indexing. Con:
  premature — there is no golden query set yet to benchmark *against*; would block Phase 1–2 on an
  experiment we can't yet measure.

## Decision
Use **`text-embedding-3-small` at 512 dimensions** as the v1 baseline. Re-examine the embedding model
as a **Phase 3 experiment** (EXP) once `recall@k` on the golden query set is measurable.

## Why the other was rejected
Benchmarking embedders before a golden set exists is tuning without a metric — exactly the thing the
learning rule forbids. The reversible move is to baseline now and run the embedder bake-off as a
logged experiment in Phase 3, deciding on the recall number.

## Consequences / what we'll measure
- `VECTOR(512)` columns; HNSW index. Re-embedding to swap models is a one-time, prompt-cacheable cost.
- Phase 3 EXP: `text-embedding-3-small` vs. ≥1 alternative on golden `recall@k`; keep/revert on number.

## Result (EXP-008, WI-7) — keep the baseline
Benchmarked `text-embedding-3-small`@512 vs `text-embedding-3-large`@512 and @1024 on golden dense
recall@k. `-3-large` lifts early-rank dense recall (recall@1 0.74→0.83, recall@3 0.93→1.00) but
**recall@5 is already 1.00 for the baseline**, and the Haiku reranker already recovers recall@1 to 0.91
end-to-end — so re-embedding buys **no pipeline-level recall** today. 512→1024 dims adds nothing.
**Decision: keep `-3-small`@512 for v1.** `-3-large`@512 (same storage) is the documented upgrade path
if the reranker is removed or dense recall@5 erodes as the corpus grows. See EXP-008.
