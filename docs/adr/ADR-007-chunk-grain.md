# ADR-007: Chunk grain for retrieval

Status: accepted
Date: 2026-06-23
Plan ref: ADR 1.2

## Context
We embed text for dense retrieval and index it for lexical retrieval. At what granularity do we
chunk SEBI circulars? Grain trades retrieval precision against context completeness.

## Options considered
- **Structure-aware clause chunks + parent-section link** — embed at clause/sub-regulation grain
  (`adj_obligation_chunk`), but keep a pointer to the parent section (`adj_obligation_section`) so the
  reasoning model can be handed the whole obligation. Pro: precision at retrieval, full context at
  synthesis (parent-document retrieval); respects legal document structure. Con: needs a structure-
  aware parser in Phase 2.
- **Whole-circular chunks** — Pro: trivial. Con: kills precision; top-k returns giant blobs; a single
  query matches a whole document regardless of which clause is relevant.
- **Fixed-token windows** — Pro: trivial, uniform. Con: shreds legal structure; a window can straddle
  two unrelated sub-regulations and split a defined term from its definition.

## Decision
**Structure-aware clause chunks with parent-section links.** Schema already separates
`adj_obligation_chunk` (fine grain, embedded) from `adj_obligation_section` (parent context).

## Why the others were rejected
Legal text is hierarchical and exact-term-sensitive; both coarse and fixed-window chunking destroy
the structure the agent relies on to cite a specific clause. The clause+parent split is the standard
parent-document-retrieval pattern and is the only one that gives precision *and* citeable context.

## Consequences / what we'll measure
- Tunable knobs (Phase 3): chunk grain (clause vs sub-regulation), parent-context size.
- Phase 3 metric: recall@k on the golden query set; chunk grain is one of the logged knobs.
