# EXP-008: Embedding bake-off — text-embedding-3-small vs -3-large (2026-07-05)

Related ADR: ADR-004 (embedding model). Plan ref: WI-7.
Dense-only recall@k on 35 golden queries, 77 obligations. In-memory (numpy cosine); production embeddings untouched.

## Hypothesis
A stronger embedding model (`-3-large`) lifts dense recall enough on this corpus to justify a one-time re-embed. Recall-first: the metric that matters is recall@k.

## Results (dense recall@k, cosine)
| model | dims | recall@1 | recall@3 | recall@5 | Δ recall@5 vs baseline |
|---|---|---|---|---|---|
| text-embedding-3-small *(baseline)* | 512 | 0.74 | 0.93 | 1.00 | +0.00 |
| text-embedding-3-large | 512 | 0.83 | 1.00 | 1.00 | +0.00 |
| text-embedding-3-large | 1024 | 0.83 | 1.00 | 1.00 | +0.00 |

## Analysis
- `-3-large` is genuinely better at **early-rank** dense retrieval: recall@1 **0.74 → 0.83**, recall@3
  **0.93 → 1.00**. That is a real model-quality lift.
- But **recall@5 is already 1.00 for the baseline** — the gold obligation is always in the top-5 dense
  pool. The pipeline consumes the reranked top-5 out of a pool of 10 (ADR-014), and the Haiku reranker
  already recovers early-rank precision on the baseline embeddings (post-rerank recall@1 **0.91**,
  recall@3 **1.00** — EXP-... / ADR-019). So the reranker already closes exactly the gap `-3-large`
  would close.
- Going from 512 → 1024 dims on `-3-large` adds **nothing** (identical recall) at 2× storage.

## Verdict
**Revert — keep `text-embedding-3-small` @ 512-dim for v1.** The `-3-large` lift is real at the dense
layer but **does not move the end-to-end number**: recall@5 is already saturated at 1.00 and the
reranker already delivers recall@1 0.91 / recall@3 1.00 on the baseline embeddings. Re-embedding the
corpus buys no pipeline-level recall today. Recorded as the cheap upgrade path: **`-3-large` @ 512-dim**
(same storage as the baseline) is the model to adopt *if* the reranker is ever removed, or if dense
recall@5 drops below 1.00 as the corpus grows — the ADR-004 re-benchmark trigger. No change to ADR-004's
v1 decision; this experiment is the evidence behind keeping it.

