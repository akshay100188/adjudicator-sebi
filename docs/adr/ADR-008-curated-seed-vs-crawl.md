# ADR-008: Corpus acquisition — curated seed vs crawler

Status: accepted
Date: 2026-06-24
Plan ref: ADR 2.1

## Context
Phase 2 ingests real SEBI text. Do we crawl sebi.gov.in or curate a bounded seed list?

## Options considered
- **Curated seed list** — a hand-picked set of circulars (the Stock Brokers master circular + the
  chain its appendix rescinds). Pro: bounded, reproducible, the whole point of a tractable prototype;
  the seed *is* the corpus boundary. Con: manual selection (one-time).
- **Crawler** — spider sebi.gov.in. Pro: breadth. Con: brittle (JS-rendered pages, PDF attachments,
  pagination), pulls in irrelevant families, and fights the bounded-corpus design. No upside for v1.

## Decision
**Curated seed list.** Anchored on the **Master Circular for Stock Brokers**
`SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (09 Aug 2024) and the running-account-settlement chapter's
rescinded-circular chain. Recorded in `data/obligations/seed_manifest.md`.

## Why the other was rejected
A crawler adds engineering risk and scope creep for zero learning benefit; the bounded corpus is a
deliberate non-goal-driven design choice (ADR-000).

## Consequences / what we'll measure
- Seed list is version-controlled and reproducible.
- Phase 2 ingest must be idempotent (re-run ≠ duplicates) — a gate metric.
