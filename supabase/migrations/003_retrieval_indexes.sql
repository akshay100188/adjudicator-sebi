-- Phase 3 retrieval indexes. Idempotent.
-- HNSW for dense (cosine), GIN for sparse (tsvector). On a 16-row corpus the planner
-- may prefer a seq scan; the indexes are here for correctness + realism as the corpus grows.

create index if not exists adj_chunk_embedding_hnsw
  on adjudicator.adj_obligation_chunk
  using hnsw (embedding extensions.vector_cosine_ops)
  with (m = 16, ef_construction = 64);

create index if not exists adj_chunk_tsv_gin
  on adjudicator.adj_obligation_chunk
  using gin (tsv);
