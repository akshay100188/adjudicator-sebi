# ADR-013: BM25 implementation — native Postgres FTS, not pg_search

Status: accepted
Date: 2026-06-24
Plan ref: ADR 3.3 · Evidence: EXP-001

## Context
Lexical retrieval can use Postgres' native full-text search (`ts_rank`/`ts_rank_cd`, TF-IDF-ish) or a
true-BM25 extension (ParadeDB / `pg_search`). The extension adds operational weight.

## Options considered
- **Native FTS (`ts_rank_cd` + `tsvector`/GIN)** — already in the schema; no new infra. EXP-001:
  sparse recall@5 = 0.93. Sufficient as the *recall* arm of hybrid (rerank fixes ranking).
- **`pg_search` / ParadeDB (true BM25)** — sharper lexical ranking; new extension to install, operate,
  and keep in sync.

## Decision
**Native Postgres FTS.** Recall-first sparse with OR-ed terms (`websearch_to_tsquery` with `OR`).

## Why the other was rejected
"Decide on a number" (plan ADR 3.3): native FTS already hits 0.93 sparse recall@5, and the reranker —
not raw lexical score — supplies final precision. A BM25 extension's sharper scores would mostly be
overwritten by rerank. Not worth the operational weight at v1 scale.

## Consequences / what we'll measure
Note: our chunk text is paraphrased obligations and contains no circular-number tokens, so the classic
"BM25 for exact circular refs" benefit doesn't apply to chunk retrieval here (circular numbers live in
`source_circular_ref` / the relation graph). Re-open this ADR if exact-token recall becomes a measured
bottleneck on a larger corpus.
