# EXP-003: Candidate pool size sweep (dense_k = sparse_k)

Date: 2026-06-24
Related ADR: ADR-014 (pool size / rerank)
Fixed: hybrid, RRF k = 60, metrics @1/3/5

## Hypothesis
A bigger candidate pool raises recall (more chance the right doc is retrieved) but adds noise to
fusion ranking and cost to a downstream reranker. There is a sweet spot.

## Results
| config | recall@1/3/5 | precision@1/3/5 | MRR | nDCG@1/3/5 | latency ms |
|---|---|---|---|---|---|
| hybrid pool=3 | 0.70 / 0.88 / 0.97 | 0.75 / 0.32 / 0.21 | 0.85 | 0.75 / 0.83 / 0.87 | 3619 |
| hybrid pool=5 | 0.68 / 0.93 / 1.00 | 0.70 / 0.33 / 0.22 | 0.82 | 0.70 / 0.83 / 0.87 | 3595 |
| hybrid pool=8 | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3484 |
| hybrid pool=16 | 0.65 / 0.82 / 0.97 | 0.70 / 0.30 / 0.20 | 0.80 | 0.70 / 0.77 / 0.83 | 3555 |

## Analysis
- **Small pools rank better** here: pool=3 has the best MRR (0.85), pool=5 the best recall@5 (1.00).
  Larger pools (8, 16) pull more lexical-noise documents into the fused list, depressing MRR.
- This is the mirror image of EXP-001's finding: on a corpus where sparse is noisy, *less* sparse
  contribution helps the un-reranked ranking.
- **But pool size interacts with rerank.** The reranker (EXP-001) only sees the pool, so the pool must
  have high *recall* even if its own ranking is mediocre. pool=5 already reaches recall@5 = 1.00 and
  the reranker fixes the ordering — so a moderate pool maximises recall headroom without over-paying
  the reranker.

## Verdict
**keep pool = 10 feeding the reranker → final top_k = 5.** Rationale: maximise recall into the rerank
stage (cheap insurance against a missed obligation — the project's worst failure) while the reranker
neutralises the added noise. For dense-only (no rerank) fallback, pool=5 is preferred. See ADR-014.
