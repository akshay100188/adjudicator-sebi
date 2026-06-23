# ADR-009: Obligation extraction — LLM + human review

Status: accepted
Date: 2026-06-24
Plan ref: ADR 2.2

## Context
Turn parsed circular text into structured obligations (text + temporal + relation metadata). Method
choice determines both data quality and whether we get a measurable gold set.

## Options considered
- **Hybrid: LLM extract → human review** — Claude proposes candidate obligations; a human approves /
  corrects. Pro: yields BOTH an extraction-accuracy metric AND the golden dataset the whole eval
  harness depends on. Con: review effort per circular.
- **Pure-auto (LLM only)** — Pro: fast. Con: unverifiable; no trustworthy gold set → the agent eval
  rests on sand.
- **Pure-manual** — Pro: accurate. Con: teaches no pipeline; doesn't scale; no extraction metric.

## Decision
**Hybrid.** LLM-assisted extraction with a human-in-the-loop review pass that is itself the gold-set
seed.

## Why the others were rejected
Pure-auto removes the verification that makes every downstream metric believable; pure-manual removes
the pipeline (and the extraction-accuracy number) that is part of the learning. Hybrid is the only
option that produces a measurable metric *and* a gold set.

## Consequences / what we'll measure
- Phase 2 gate: extraction accuracy vs. the hand-reviewed sample ≥ threshold (set when first chapter
  is extracted).
- The reviewed obligations become `eval/golden/` seeds for recall@k and finding P/R.
