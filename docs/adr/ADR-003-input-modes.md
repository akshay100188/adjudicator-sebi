# ADR-003: Input modes for v1

Status: accepted
Date: 2026-06-23
Decision ref: §10 Decision B

## Context
The system accepts two kinds of input: a structured **scenario** (a product-change description with
fields) and an uploaded **document** (a policy PDF/HTML). Each adds work; we must sequence them so we
reach a *measurable engine* fastest.

## Options considered
- **Scenario-only first** — structured input in → cited findings out. Pro: fastest path to a
  measurable engine; no PDF/HTML parsing or upload-PII handling blocking the core agent; smallest
  provable increment. Con: less complete demo until document upload lands.
- **Both from the start** — scenario + document upload together. Pro: more complete demo sooner.
  Con: adds parsing + ephemeral-upload PII handling (§3) *before* the core agent is even measured;
  larger surface to debug at once.

## Decision
**Scenario-only first.** Document upload is added after the agent + eval harness are proven.

## Why the other was rejected
Doing both up front front-loads parsing and PII plumbing onto the critical path of the thing we
actually want to learn and measure (the agent + retrieval). Scenario input exercises the entire
agent loop and synthesis with none of that overhead, so we can hit the Phase 3/4/5 metric gates
sooner, then add documents as an input adapter that feeds the same engine.

## Consequences / what we'll measure
- Phase 5 findings P/R and citation-faithfulness are measured on **scenarios** first.
- Document upload, when added, must reuse the same agent + synthesis path and obey §3 PII rules:
  process ephemerally, never persist the raw upload, store only derived finding metadata.
