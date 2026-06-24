# ADR-015: Evaluation methodology — metrics, judge, tracer, regression gate

Status: accepted
Date: 2026-06-24
Plan ref: §6, §7, Phase 6

## Context
An agent must be judged on its *path*, not just its *answer* (§7). We need a reproducible harness
covering retrieval, findings, and trajectories — and a gate so tuning can't silently regress.

## Decisions
1. **Offline metrics first** (deterministic, free, reproducible): recall@k / precision@k / MRR / nDCG
   for retrieval; finding precision/recall + citation-faithfulness for gap detection (Phase 5);
   tool-selection accuracy + trajectory match + correction-trigger correctness for the agent (§7).
2. **LLM-as-judge** for finding *quality* only, always anchored to a human-labelled slice (bias guard).
   Not used where a deterministic metric exists.
3. **Tracer = custom JSON trajectory log** (the `docs/trajectories/` template + per-run logs), not
   LangSmith/Phoenix. Rationale: the hand-rolled agent (ADR-002) already owns its loop; a lightweight
   self-logged trajectory is enough to *show* the agentic-ness and is zero-dependency. LangSmith/
   Phoenix noted as the natural upgrade if we want a hosted trace UI.
4. **Metric suite = custom (this harness)** for now; RAGAS/DeepEval noted for faithfulness/context
   metrics once Phase 5 findings exist.
5. **Regression gate on recall** (`eval/regression_gate.py`): runs deterministic hybrid retrieval (no
   rerank — recall is a pool property; rerank affects ranking) and fails CI if recall@5 < 0.95,
   recall@3 < 0.80, recall@1 < 0.45. Recall-first: the gate protects against the worst failure.

## Why others were rejected (for now)
A hosted tracer (LangSmith/Phoenix) and a full metric suite (RAGAS) add dependencies before we have a
trajectory or a finding to measure; they're deferred to when there's data to put through them. Gating
on a rerank-based metric would make the gate slow (LLM calls) and nondeterministic.

## Consequences / what we'll measure
- `eval/harness.py` (metrics + trajectory metrics), `eval/golden/{queries,scenarios,trajectories}.jsonl`,
  `eval/regression_gate.py`.
- Gate currently PASSES at 54-obligation scale (recall@5 0.99).
- Trajectory + finding evals are wired and populate once Phase 4 (agent) and Phase 5 (synthesis) land.
