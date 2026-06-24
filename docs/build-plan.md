# Build Plan (phased)

Per-phase skeleton: **Objective · Build · ADRs · Tunable knobs · Metric gate · Interview defense.**

**Decision-gate protocol (non-negotiable):** every `🦦 GATE` is a PO decision. At each gate Claude
Code states the decision in one line, presents 2–4 real options (gives/costs/when-right), gives a
recommendation with reasoning, then **stops for sign-off**. No building past an unsigned gate.

**Build order (smallest provable increments):**
`0 → 1 → 2 → 3 (tools, measured) → 6 (eval harness, early) → 4 (agent) → 5 (synthesis) → 7 (UI) → 8 (stretch)`
Note the deliberate inversion: **the eval harness comes before the agent** — you cannot tune an
agent you can't measure, and trajectory eval is what makes the agentic claim defensible.

---

## Phase 0 — Foundations & framing  ✅ (this commit)
Repo skeleton; ADR/experiment/trajectory logging; scope + metrics locked; showcase thesis drafted.
GATE (signed): corpus boundary = Stock Brokers (ADR-001); agent framework = hand-rolled (ADR-002).

## Phase 1 — Corpus & data model  ✅
Clean, structured, temporally-correct obligations + relations.
- Schema in `supabase/migrations/001_schema.sql` (isolated `adjudicator` schema, `adj_` tables).
- `adj_obligation`, `adj_obligation_section`, `adj_obligation_relations` (T4 citation graph),
  `adj_obligation_chunk` (clause grain + parent link).
- SQL functions: `adj_valid_obligations(as_of, family)` (T1 temporal validity),
  `adj_relation_closure(start_ref, ...)` (recursive supersession traversal).
- ADR-006 (relations table, not GraphRAG); ADR-007 (clause chunk grain).
- **Gate PASSED:** temporal validity correct at 3 dates; recursive closure walks the chain; 100%
  temporal-metadata resolution. Proven by `scripts/validate_phase1.py` against the live DB.

## Phase 2 — Ingestion pipeline  ✅
Fetch (curated seed) → parse → LLM-assisted extract (human review = gold seed) → relation edges from
footnotes → embed + index (pgvector + tsvector). Idempotent.
- ADR-008 (curated seed), ADR-009 (hybrid extraction), ADR-010 (contextual = Phase 3 experiment).
- Ingested: chapter 47 (running-account settlement) of Stock Brokers master circular 2024/110 →
  **16 obligations** (human-reviewed: 9 verbatim, 4 split/reframed), **6 real relation edges**,
  16 embedded chunks. Source PDFs in data/raw (gitignored, not redistributed).
- **Gate PASSED:** extraction faithful vs. human review; idempotent re-run (16/9/16 stable);
  graph closure traverses the full supersession chain; dense search returns relevant obligations.
- Contextual enrichment (`context_blurb`) left off — A/B'd in Phase 3 (ADR-010).

## Phase 3 — Retrieval substrate (the agent's tools)  ◑ tools + experiments done; contextual EXP pending
T1 temporal_filter · T2 hybrid_search (dense⊕BM25, RRF) · T3 expand_to_parent · T4 graph_lookup ·
T5 rerank — all built in `backend/app/tools/`.
- Experiments (20-query golden set): EXP-001 retriever comparison, EXP-002 RRF k, EXP-003 pool size.
- ADRs locked: ADR-011 (hybrid+rerank), ADR-012 (RRF k=60), ADR-013 (native FTS BM25), ADR-014 (Haiku rerank, pool=10→top5).
- **Gate PASSED:** recall@5 = 1.00, MRR 0.97 (hybrid+rerank) on the golden set; every knob logged.
- Remaining: EXP for contextual enrichment on/off (ADR-010); embedding-model benchmark (ADR-004).

## Phase 6 — Eval harness (built early, formalised here)  ◑ harness + gate done; finding/trajectory eval wired
Golden dataset (gold queries → expected obligations; gold scenarios → expected findings; gold
trajectories → expected tool sequence); automated runner; regression gate.
- `eval/harness.py` (retrieval + trajectory metrics), `eval/golden/{queries,scenarios,trajectories}.jsonl`
  (35 queries · 6 scenarios incl. a compliant no-gap control · 4 trajectories), `eval/regression_gate.py`.
- ADR-015 eval methodology (offline-first, LLM-judge for finding quality only, custom JSON tracer,
  recall regression gate). **Gate PASSES** at 54-obligation scale (recall@5 0.99).
- Finding eval (Phase 5) + trajectory eval (Phase 4) populate when those phases land.

## Phase 4 — The agent
Hand-rolled ReAct loop; tool schemas; system prompt; loop governance. Behaviours: routing/adaptive,
decomposition, multi-hop, corrective (CRAG), self-reflection (Self-RAG grounding gate).
- Gate: trajectory correct on golden set + end-answer recall ≥ target.

## Phase 5 — Gap-detection / grounded synthesis
Sonnet (prompt-cached) → structured findings (gap_summary, evidence, recommended_action,
obligation_citation, confidence). Grounding contract: may only cite obligations actually passed.
- Gate: finding P/R; citation faithfulness ≥ threshold; cost/run within budget.

## Phase 7 — Interface & showcase
Next.js: obligation browser, scenario runner, findings w/ citations, review queue, **agent-trajectory
viewer**. Showcase writeup (why-not-production thesis, architecture decisions, eval table).

## Phase 8 — Code-analysis module (stretch)
Semgrep + AST + tree-sitter → Haiku consolidation (metadata only) → agent maps to obligations.
Privacy-by-design. Only after agent + eval are solid (ADR-005).
