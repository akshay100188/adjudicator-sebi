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
