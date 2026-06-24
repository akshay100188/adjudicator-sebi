# EXP-001: Retriever comparison — dense vs sparse vs hybrid vs hybrid+rerank

Date: 2026-06-24
Related ADR: ADR-011 (retrieval architecture), ADR-013 (BM25 impl), ADR-014 (rerank)
Corpus: chapter 47, 16 obligations · Golden set: 20 queries (paraphrase / exact-term / multi)
Fixed: candidate pool = 10, RRF k = 60, metrics @1/3/5

## Hypothesis
Hybrid (dense ⊕ BM25, RRF) beats either retriever alone on a legal corpus that needs both meaning
and exact terms; a reranker further lifts precision/ranking.

## Results
| config | recall@1/3/5 | precision@1/3/5 | MRR | nDCG@1/3/5 | latency ms |
|---|---|---|---|---|---|
| dense | 0.80 / 0.93 / 1.00 | 0.85 / 0.33 / 0.22 | 0.90 | 0.85 / 0.88 / 0.92 | 1854 |
| sparse (BM25-ish, native FTS) | 0.38 / 0.72 / 0.93 | 0.40 / 0.27 / 0.20 | 0.61 | 0.40 / 0.59 / 0.68 | 1792 |
| hybrid RRF(k=60) | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3564 |
| **hybrid + Haiku rerank** | **0.90 / 1.00 / 1.00** | 0.95 / 0.37 / 0.22 | **0.97** | 0.95 / 0.98 / 0.98 | 7859 |

## What actually happened (the honest read)
1. **Dense is strong on this corpus** (MRR 0.90, recall@5 1.00). The obligations are semantically
   distinct paraphrases; embeddings separate them well.
2. **Sparse alone is weak on ranking** (MRR 0.61). OR-ed lexical matching over-returns documents that
   merely share common tokens ("client", "settlement") — recall@5 is decent (0.93) but the right doc
   often isn't first.
3. **Naive hybrid is WORSE than dense on ranking** (MRR 0.79 vs 0.90). This is the important, non-
   obvious finding: RRF gives sparse's noisy top results equal rank-weight to dense's sharp ones, so
   fusion *dilutes* a strong dense signal on a corpus where dense is already good and sparse is noisy.
4. **Rerank is the decisive component.** Haiku reranking the hybrid candidate pool lifts MRR 0.79→0.97
   and precision@1 0.70→0.95, and recovers recall@3 to 1.00. The recall-first pool guarantees the
   right obligation is *in* the candidate set; the reranker puts it on top.

## Latency note (not a retrieval-quality finding)
Per-query latency is dominated by **per-call connection setup to the remote Supabase pooler**
(ap-northeast-2), not search compute (16 rows). Dense = 1 round-trip (~1.8s), hybrid = 2 (~3.5s),
+rerank adds one Haiku call (~4s). Connection pooling is a cheap future win; it does not affect the
parameter choice.

## Verdict
**keep — hybrid candidate generation + Haiku rerank.** Best measured recall AND ranking. Dense-only is
recorded as a strong, cheap baseline (no LLM, ~4x faster) and a valid fallback. The value of *hybrid*
over dense is exact-term coverage (see Q03/Q20) and future-proofing as the corpus grows and dense
alone degrades; the value of *rerank* is precision. See ADR-011.

## Caveat (corpus size)
16 obligations in one chapter → metrics saturate (recall@5 reaches 1.00 easily). Treat these as a v1
baseline. The decisive re-test is after more chapters are ingested, where lexical exact-match and the
embedding-model choice (ADR-004 benchmark) matter more.
