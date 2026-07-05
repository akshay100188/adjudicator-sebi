# ADR-019: Two-tier recall protection — deterministic pool gate + periodic post-rerank eval

Status: accepted
Date: 2026-07-04
Plan ref: Phase 7 WI-1 · Evidence: eval/reports/rerank_recall_2026-07-04.md, ADR-014, ADR-015

## Context
The regression gate (ADR-015, `eval/regression_gate.py`) runs deterministic hybrid retrieval **without**
rerank and asserts recall thresholds in CI. That is correct as a tripwire — fast, free, deterministic —
but it measures **raw pool recall**. The agent does not consume the raw pool: it consumes the
**reranked top-5 out of a pool of 10** (ADR-014). Those are different numbers. The Haiku reranker can
reorder a gold obligation out of the top-5, and the gate never runs the reranker, so a reranker
regression that silently drops a real obligation would pass CI unnoticed — a false negative, the worst
failure mode in a compliance tool.

## Options considered
- **Put rerank in the CI gate** — measures what the agent consumes, but makes CI nondeterministic
  (Haiku), slow, and cost-bearing on every run. Flaky gates get ignored; recoverable determinism lost.
- **Trust pool recall as a proxy** — cheap, but it is provably not the number the agent experiences;
  the whole point of rerank is to reorder, which can move gold across the top-k boundary.
- **Two tiers (chosen)** — keep the deterministic pool-recall gate exactly as-is in CI, and add a
  separate, lower-frequency **post-rerank recall eval** (`eval/rerank_recall_eval.py`) that runs the
  same `hybrid_search` + `rerank` tools the agent calls, computes post-rerank recall@{1,3,5}, emits a
  delta vs pool recall, and logs every **rerank drop** (gold in the raw pool but out of the reranked
  top-k). Run on demand / nightly / pre-release, never in CI.

## Decision
**Two-tier recall protection.** Tier 1: the deterministic pool-recall gate stays the CI tripwire
(unchanged). Tier 2: the periodic post-rerank eval guards the recall the agent actually consumes and
surfaces the drops the gate structurally cannot see. The split is deliberate: cheap determinism guards
the pool, an honest LLM-based eval guards the consumed number.

## Why the others were rejected
Folding rerank into CI trades a real, cheap, deterministic guarantee for a flaky, paid one — and a
flaky gate is worse than no gate because teams learn to override it. Trusting pool recall as a proxy
ignores that rerank's entire job is to reorder, which is exactly the operation that can move a gold
obligation across the top-5 boundary. The two-tier split keeps CI honest *and* measures the number the
agent lives on.

## Consequences / what we'll measure
- **First run (2026-07-04, 35 golden queries):** post-rerank recall@{1,3,5} = **0.91 / 1.00 / 1.00**
  vs raw-hybrid pool **0.60 / 0.84 / 0.99** — deltas **+0.31 / +0.16 / +0.01**. **Zero rerank drops.**
  The reranker is faithful: it reorders for precision (recall@1 0.60→0.91) without costing recall, and
  even recovers one gold obligation from pool ranks 6–10 into the top-5 (Q18: pool recall@5 0.50 →
  post-rerank 1.00).
- **Gate on the drop list:** if a future run shows post-rerank recall@5 materially below pool recall@5,
  or any nonzero drop list, treat it as a reranker regression and surface it before any release/writeup
  claims a recall number.
- Runs out of CI (Haiku, nondeterministic, paid). ~$0.03/run at 35 queries.
