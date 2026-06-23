# ADR-001: v1 corpus boundary — which SEBI regulation family

Status: accepted
Date: 2026-06-23
Decision ref: §10 Decision A

## Context
The corpus must be tractable and the golden set buildable by a solo developer. One regulation
family is enough to prove the engine. The family chosen also determines how good a showcase the
**agentic supersession-tracing** story can be — the whole reason the project is agentic.

## Options considered
- **Stock Brokers** — the flagship multi-hop example (running-account settlement of client funds)
  lives here. Rich amend/supersede chains and master-circular consolidation. Pro: best demonstration
  of the core differentiator (multi-hop + temporal + citation graph). Con: more relation edges to
  seed correctly.
- **Investment Advisers** — smaller, cleaner corpus (IA Regulations + circulars). Pro: less ingest
  effort. Con: fewer supersession chains → the multi-hop agent has less to trace → weaker demo.
- **LODR** — Listing Obligations & Disclosure Requirements. Pro: strong for cross-reference
  following. Con: large, dense, heavily cross-referenced → heavier to ingest and gold-label for v1.

## Decision
**Stock Brokers** family for v1.

## Why the others were rejected
Investment Advisers under-exercises the agentic behaviours that are the point of the project — with
few supersession chains, `graph_lookup` and corrective re-retrieval rarely fire, so the trajectory
eval has little to show. LODR is the opposite problem: its size and cross-reference density make a
correct, hand-verified gold set too expensive for a v1 solo build. Stock Brokers sits in the sweet
spot — enough supersession/consolidation to make the multi-hop story real, small enough to gold-label.

## Consequences / what we'll measure
- Phase 1 metric gate: ≥ X% of seeded Stock Brokers obligations have resolved temporal metadata;
  relation edges spot-check correctly to source (threshold set in Phase 1 spec).
- Corpus seed list (curated, not crawled — ADR-002-ingest) drawn from sebi.gov.in *Legal* section:
  Stock Brokers master circular(s) + the base/amending circulars their appendices rescind.
