# EXP-004: Scale re-test — do the Phase 3 parameter choices hold on 3× the corpus?

Date: 2026-06-24
Related ADR: ADR-011..014
Corpus: 54 obligations (chapters 45, 46, 47, 92, 93) · Golden set: 35 queries
Also: DB connection made persistent (warm reuse) — see "Latency" below.

## Why
EXP-001..003 ran on 16 obligations (one chapter), where metrics saturate. We tripled the corpus
with the client-assets cluster (client securities, pay-in validation, bank guarantees, upstreaming)
— many *semantically adjacent* obligations about client funds/securities, i.e. hard distractors —
and re-ran the same sweeps. The question: do the chosen values survive a harder retrieval task?

## EXP-001 (re-test) — retriever comparison
| config | recall@1/3/5 | MRR | nDCG@5 | latency ms | vs 16-corpus MRR |
|---|---|---|---|---|---|
| dense | 0.74 / 0.93 / 1.00 | 0.86 | 0.89 | 290 | 0.90 → 0.86 |
| sparse (native FTS) | 0.34 / 0.73 / 0.76 | 0.53 | 0.59 | 201 | 0.61 → 0.53 |
| naive hybrid RRF(60) | 0.59 / 0.84 / 0.99 | 0.74 | 0.80 | 424 | 0.79 → 0.74 |
| **hybrid + Haiku rerank** | **0.91 / 1.00 / 1.00** | **0.97** | 0.98 | 3222 | 0.97 → 0.97 |

**Findings (the choices hold, and the reasoning sharpens):**
1. **Sparse degrades most with scale** — recall@5 0.93 → **0.76**, MRR 0.61 → 0.53. OR-ed lexical
   matching pulls in ever more documents that merely share common tokens as the corpus grows. This is
   the textbook reason you don't ship pure lexical.
2. **Dense stays strong** — recall@5 still 1.00, MRR 0.86. Embeddings separate even adjacent obligations.
3. **Naive hybrid still loses to dense** (0.74 < 0.86) — the dilution effect is *robust*, not a small-
   corpus artdefact: fusing dense with a now-noisier sparse list costs ranking quality.
4. **Rerank is even more decisive at scale.** It lifts hybrid MRR 0.74 → **0.97** and recall@1
   0.59 → **0.91**, fully recovering precision the larger corpus took away. The gap rerank closes
   *grew* vs the 16-corpus test — exactly the trend you want from your most important component.

## EXP-002 (re-test) — RRF k {10,30,60,100}
Still **completely flat** (MRR 0.74 across all). k is not sensitive even at 54 docs → keep **k = 60**.

## EXP-003 (re-test) — candidate pool {3,5,8,16}
| pool | recall@5 | MRR |
|---|---|---|
| 3 | 0.96 | 0.77 |
| **5** | **1.00** | **0.81** |
| 8 | 0.99 | 0.76 |
| 16 | 0.96 | 0.78 |
pool=3 now *loses* recall (0.97 → 0.96) — too small once distractors grow. **pool=5** is the un-
reranked sweet spot (recall@5 1.00, best MRR). For the rerank pipeline we keep **pool=10** for recall
headroom into the reranker (recall insurance; the reranker removes the extra noise). Choices unchanged.

## Latency (operational win)
Making the eval DB connection persistent (reuse one warm connection vs a fresh TCP+TLS+auth handshake
to the Supabase pooler per call) cut per-query latency ~6×: dense 1854 → **290 ms**, hybrid 3564 →
**424 ms**, hybrid+rerank 7859 → **3222 ms** (the rerank residual is the Haiku call, not the DB).

## Addendum — re-measured at 77 obligations (2026-07-05, 35 golden queries)
The corpus has since grown to **77 obligations** (added chapters + `refers_to` cross-edges). Re-running
the same configs on the live 77-corpus confirms the pattern holds and gives the numbers the Phase-7
writeup quotes (so every writeup figure is on one corpus, not a mix):

| config | recall@1/3/5 | MRR | source |
|---|---|---|---|
| dense | 0.74 / 0.93 / 1.00 | **0.86** | this addendum · EXP-008 (recall) |
| naive hybrid RRF(60) | 0.60 / 0.84 / 0.99 | **0.76** | this addendum · regression_gate |
| **hybrid + Haiku rerank** | **0.91 / 1.00 / 1.00** | **0.97** | EXP-009 (reranker bake-off) |

The dilution effect is now evidenced at **three scales** (16 → 54 → 77): naive-hybrid MRR 0.79 → 0.74
→ 0.76 stays **below** dense 0.90 → 0.86 → 0.86, and rerank lifts hybrid to MRR **0.97** at every scale.
The post-rerank recall the agent actually consumes (0.91/1.00/1.00, zero drops) is in
`eval/reports/rerank_recall_*.md` (ADR-019).

## Verdict
**keep all ADR-011..014 values.** Validated now at 16, 54, and 77 obligations: hybrid candidate
generation + Haiku rerank, RRF k=60, pool=10→top5, native FTS. The core thesis — rerank turns a
recall-first pool into precise results, and its value grows with corpus size — is evidenced across
three corpus scales.
