-- Project Adjudicator (SEBI) — Phase 1 schema
-- Isolated schema on a shared Supabase project. Nothing here touches `core.*`,
-- `screener.*`, or `public.*`. All app tables prefixed `adj_`.
--
-- Correctness backbone: temporal validity + typed supersession edges.
-- ADR-001 (Stock Brokers), ADR 1.1 (relations table, not GraphRAG), ADR 1.2 (clause chunks).

create schema if not exists adjudicator;

-- pgvector lives in the `extensions` schema on Supabase; reference the type qualified.
create extension if not exists vector with schema extensions;

-- ---------------------------------------------------------------------------
-- Parent sections (parent-document retrieval: embed clause, return section)
-- ---------------------------------------------------------------------------
create table if not exists adjudicator.adj_obligation_section (
  section_id   text primary key,
  circular_ref text not null,
  heading      text,
  full_text    text not null,
  created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Atomic obligations (clause grain) with temporal + provenance metadata
-- ---------------------------------------------------------------------------
create table if not exists adjudicator.adj_obligation (
  obligation_id     text primary key,
  obligation_text   text not null,
  source_circular_ref text not null,
  source_url        text not null,
  issue_date        date not null,
  effective_date    date not null,
  superseded_by     text references adjudicator.adj_obligation(obligation_id),
  regulation_family text not null default 'stock_brokers',
  intermediary_type text,
  category          text,
  parent_section_id text references adjudicator.adj_obligation_section(section_id),
  is_synthetic      boolean not null default false,  -- true for structural test fixtures
  created_at        timestamptz not null default now()
);

create index if not exists adj_obligation_family_idx
  on adjudicator.adj_obligation (regulation_family);
create index if not exists adj_obligation_effective_idx
  on adjudicator.adj_obligation (effective_date);
create index if not exists adj_obligation_superseded_idx
  on adjudicator.adj_obligation (superseded_by);

-- ---------------------------------------------------------------------------
-- The narrow citation graph behind tool T4 (NOT GraphRAG — ADR 1.1).
-- Seeded from master-circular appendices (the rescinded-circular lists).
-- ---------------------------------------------------------------------------
create table if not exists adjudicator.adj_obligation_relations (
  from_ref      text not null,
  to_ref        text not null,
  relation_type text not null check (relation_type in
                  ('amends','supersedes','refers_to','consolidated_by')),
  source_note   text,
  created_at    timestamptz not null default now(),
  primary key (from_ref, to_ref, relation_type)
);

create index if not exists adj_relations_from_idx
  on adjudicator.adj_obligation_relations (from_ref);
create index if not exists adj_relations_to_idx
  on adjudicator.adj_obligation_relations (to_ref);

-- ---------------------------------------------------------------------------
-- Retrieval chunks (clause grain) linked to parent section.
-- embedding + tsv populated in Phase 2/3; HNSW + GIN indexes added in Phase 3.
-- ---------------------------------------------------------------------------
create table if not exists adjudicator.adj_obligation_chunk (
  chunk_id      text primary key,
  obligation_id text references adjudicator.adj_obligation(obligation_id),
  section_id    text references adjudicator.adj_obligation_section(section_id),
  chunk_text    text not null,
  context_blurb text,                      -- Phase 2 contextual enrichment
  embedding     extensions.vector(512),    -- Phase 2/3
  tsv           tsvector,                  -- Phase 3 (BM25-ish lexical)
  created_at    timestamptz not null default now()
);

create index if not exists adj_chunk_obligation_idx
  on adjudicator.adj_obligation_chunk (obligation_id);

-- ===========================================================================
-- Tool T1 substrate: temporal validity. An obligation is valid-as-of D if it
-- is effective by D and not yet superseded by something effective by D.
-- ===========================================================================
create or replace function adjudicator.adj_valid_obligations(
  as_of date,
  family text default null
)
returns setof adjudicator.adj_obligation
language sql stable as $$
  select o.*
  from adjudicator.adj_obligation o
  where o.effective_date <= as_of
    and (family is null or o.regulation_family = family)
    and (
      o.superseded_by is null
      or not exists (
        select 1 from adjudicator.adj_obligation s
        where s.obligation_id = o.superseded_by
          and s.effective_date <= as_of
      )
    );
$$;

-- ===========================================================================
-- Tool T4 substrate: recursive traversal of the citation graph. Proves we
-- handle supersession chains with recursive SQL — no graph database needed.
-- ===========================================================================
create or replace function adjudicator.adj_relation_closure(
  start_ref  text,
  rel_types  text[] default array['supersedes','amends','consolidated_by'],
  max_depth  int default 10
)
returns table(from_ref text, to_ref text, relation_type text, depth int)
language sql stable as $$
  with recursive walk as (
    select r.from_ref, r.to_ref, r.relation_type, 1 as depth
    from adjudicator.adj_obligation_relations r
    where r.from_ref = start_ref
      and r.relation_type = any(rel_types)
    union all
    select r.from_ref, r.to_ref, r.relation_type, w.depth + 1
    from adjudicator.adj_obligation_relations r
    join walk w on r.from_ref = w.to_ref
    where r.relation_type = any(rel_types)
      and w.depth < max_depth
  )
  select walk.from_ref, walk.to_ref, walk.relation_type, walk.depth
  from walk;
$$;
