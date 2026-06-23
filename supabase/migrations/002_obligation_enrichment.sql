-- Phase 2 enrichment: fields produced by LLM extraction + human review.
-- Idempotent.

alter table adjudicator.adj_obligation
  add column if not exists title           text,
  add column if not exists clause_refs     text[],
  add column if not exists expected_controls jsonb;
