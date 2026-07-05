# EXP-009: Reranker bake-off — Haiku vs cross-encoder (2026-07-05)

Related ADR: ADR-014 (reranker & pool). Plan ref: WI-7.
Same hybrid pool of 10 -> top-5, 35 golden queries.

## Hypothesis
A dedicated cross-encoder (attends to query+passage jointly) might beat the Haiku LLM reranker on ranking quality and/or latency. Haiku is the incumbent — only switch on a measured win.

## Results
| reranker | MRR | precision@1 | recall@1/3/5 | latency ms/q |
|---|---|---|---|---|
| Haiku (incumbent) | 0.97 | 0.94 | 0.91/1.00/1.00 | 2392 |
| Cross-encoder (ms-marco-MiniLM-L-6-v2) | 0.97 | 0.94 | 0.91/1.00/1.00 | 92 |

## Analysis
- **Ranking quality is a dead heat.** Both rerankers land identical MRR 0.97, precision@1 0.94, and
  recall@1/3/5 0.91/1.00/1.00 on the golden set. On this corpus the cross-encoder gives **no quality
  win** over the Haiku LLM reranker — the thing ADR-014 said to switch on does not exist here.
- **The cross-encoder is far cheaper on latency and money.** 92 ms/query vs Haiku's 2392 ms/query
  (~26× faster; the Haiku figure is one LLM round-trip) and **zero marginal API cost** (local inference).
- **But it costs operational weight.** It pulls in `sentence-transformers` + PyTorch (~2 GB) and a
  model download/cold-start — against a stack (ADR-013/014) that is deliberately all-API and lean.

## Verdict
**Keep Haiku for v1 — but the cross-encoder is now a *measured* upgrade, not a guess.** There is no
quality reason to switch (identical MRR 0.97). The cross-encoder's real advantage is latency/cost, and
rerank latency is **not** the bottleneck in a ~30–60 s agent loop — so adding a 2 GB torch dependency to
a prototype whose discipline is "no disproportionate operational weight" is not justified today.
Recorded as the clear **scale/latency lever**: if reranking ever becomes volume- or latency-bound
(batch document analysis, cost pressure, a synchronous UX budget), `ms-marco-MiniLM-L-6-v2` is a drop-in
that matches Haiku's ranking at ~26× the speed and no per-call cost. ADR-014's incumbent decision stands;
this experiment is the evidence that switching is a one-line change the day it matters.

