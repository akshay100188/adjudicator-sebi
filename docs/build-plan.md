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

## Phase 2 — Ingestion pipeline  ⏳ corpus locked; ingestion run blocked on API keys
Fetch (curated seed) → parse → LLM-assisted extract (human-in-the-loop = gold seed) → extract
relations from appendix rescinded-lists → contextual enrichment → embed + index (pgvector + tsvector).
- Decisions locked: ADR-008 (curated seed), ADR-009 (hybrid extraction), ADR-010 (contextual = Phase 3 experiment).
- Seed corpus locked: `data/obligations/seed_manifest.md` (Stock Brokers master circular 2024/110 +
  running-account-settlement chapter + rescinded chain).
- Gate: extraction accuracy ≥ threshold; idempotent (re-run ≠ duplicates).
- **Blocked on:** `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` in `backend/.env`.

## Phase 3 — Retrieval substrate (the agent's tools)
T1 temporal_filter · T2 hybrid_search (dense⊕BM25, RRF) · T3 expand_to_parent · T4 graph_lookup ·
T5 rerank. ADR-dense: hybrid vs pure; pre-filter; BM25 impl (ts_rank vs pg_search); rerank choice.
- Gate: recall@k hits target; precision/nDCG tracked; every knob change logged.

## Phase 6 — Eval harness (built early, formalised here)
Golden dataset (gold queries → expected obligations; gold scenarios → expected findings; gold
trajectories → expected tool sequence); automated runner; regression gate.

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
