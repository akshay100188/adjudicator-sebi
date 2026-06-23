# ADR-006: Citation graph — relations table vs GraphRAG vs graph DB

Status: accepted
Date: 2026-06-23
Plan ref: ADR 1.1

## Context
The agent must trace amends / supersedes / refers_to / consolidated_by relationships to reach the
*consolidated* position on a topic (tool T4). How should those relationships be stored and traversed?

## Options considered
- **Narrow relations table + recursive SQL** — typed edges in `adj_obligation_relations`, traversed
  with a `WITH RECURSIVE` query. Pro: edges are a handful of typed rows seeded directly from SEBI's
  own master-circular appendices (the published rescinded-circular lists); recursive SQL handles
  chain-following; zero new infrastructure. Con: not suited to open-ended "global sensemaking" graph
  queries.
- **GraphRAG (Microsoft)** — LLM-built entity graph + community summaries (Leiden clustering). Pro:
  powerful for global sensemaking. Con: LLM-heavy to index and re-index; disproportionate for a
  single regulator with a handful of explicit, authoritative edge types.
- **Dedicated graph DB (Neo4j)** — Pro: native traversal. Con: a whole new datastore + sync burden
  for what is a few hundred typed edges that Postgres traverses fine.

## Decision
**Narrow relations table + recursive SQL.** Implemented as `adj_obligation_relations` +
`adj_relation_closure()` (validated in `scripts/validate_phase1.py`).

## Why the others were rejected
The relationships here are *authoritative and explicit* — SEBI publishes the rescinded list in each
master circular's appendix. We don't need an LLM to infer a graph (GraphRAG) or a separate engine to
store one (Neo4j); we need to faithfully record published edges and walk them. GraphRAG is noted as a
future *blog-post comparison*, not a build.

## Consequences / what we'll measure
- Traversal correctness proven by the Phase 1 gate (closure reaches the full synthetic chain).
- Phase 2 metric: relation-edge accuracy ≥ 95% vs. hand-checked appendix sources.
