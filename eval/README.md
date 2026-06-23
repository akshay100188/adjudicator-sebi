# eval

The eval harness (Phase 6, built early). Holds:
- `golden/queries.jsonl` — gold queries → expected obligations (recall@k).
- `golden/scenarios.jsonl` — gold scenarios → expected findings (finding P/R, faithfulness).
- `golden/trajectories.jsonl` — gold tool sequences (trajectory match, §7).
- `runner.py` — prints recall@k, precision, nDCG, finding P/R, faithfulness, trajectory metrics, cost.
- `runs/` — per-run artifacts (gitignored).

Regression gate: tuning must not silently degrade recall. See `docs/metrics.md`.
