# EXP-002: RRF k (rank-fusion constant) sweep

Date: 2026-06-24
Related ADR: ADR-012 (RRF k)
Fixed: hybrid, pool = 10, metrics @1/3/5

## Hypothesis
The RRF constant k (in score = Σ 1/(k + rank)) trades emphasis on top ranks (small k) vs flatter
fusion (large k); some value should be best.

## Results
| config | recall@1/3/5 | precision@1/3/5 | MRR | nDCG@1/3/5 | latency ms |
|---|---|---|---|---|---|
| hybrid RRF(k=10) | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3543 |
| hybrid RRF(k=30) | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3533 |
| hybrid RRF(k=60) | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3548 |
| hybrid RRF(k=100) | 0.65 / 0.82 / 0.93 | 0.70 / 0.30 / 0.20 | 0.79 | 0.70 / 0.77 / 0.81 | 3645 |

## Analysis
**Completely flat.** With only two ranked lists and a small candidate pool, k changes the absolute
fused scores but not the *relative order* enough to move any document across the @1/3/5 boundaries.
k is not a sensitive knob at this corpus size.

## Verdict
**keep k = 60** — the literature-standard default. No evidence to deviate; revisit only if a larger
corpus shows sensitivity. See ADR-012.
