# ADR-010: Contextual Retrieval — on/off as a measured experiment

Status: accepted
Date: 2026-06-24
Plan ref: ADR 2.3

## Context
Anthropic's Contextual Retrieval prepends a short LLM-generated blurb situating each chunk in its
parent circular before embedding/BM25 indexing, reportedly cutting failed retrievals. Adopt it
blindly, or prove the lift?

## Options considered
- **Build the hook, decide on a number (Phase 3 experiment)** — implement `context_blurb` generation
  but A/B it against no-blurb on golden recall before defaulting it on. Pro: obeys the learning rule
  (no knob tuned without a metric); honest. Con: defers the on/off decision.
- **Assume on** — Pro: simplest. Con: tuning without a metric; can't defend the choice.
- **Skip it** — Pro: cheaper ingest. Con: leaves a known, citable recall lever unused, untested.

## Decision
Implement the `context_blurb` column + generation hook now (schema already has the column); **decide
on/off via a logged Phase 3 experiment** measuring recall@k lift.

## Why the others were rejected
Assuming-on violates the project's core rule; skipping forgoes a measurable lever without evidence.

## Consequences / what we'll measure
- Phase 3 EXP: contextual-on vs contextual-off recall@k on the golden query set; keep/revert on number.
- One-time, prompt-cacheable ingest cost when enabled.

## Result (EXP-007, WI-7) — off for v1, ready as a lever
Measured contextual-on vs -off dense recall@k: prepending an LLM situating blurb lifts recall@1
0.74→0.79 and recall@3 0.93→0.99, with **recall@5 unchanged at 1.00**. Real but modest; the reranked
pipeline already delivers recall@1 0.91 / recall@3 1.00 on plain chunks, so it does not move the
end-to-end number today. **Decision: off for v1** (simplicity), but it never hurts recall and is a
one-time ingest cost — so it is the **first lever to enable** if dense recall@5 drops as the corpus
grows, ahead of the heavier embedding swap (EXP-008). "Decide on the number" is now decided. See EXP-007.
