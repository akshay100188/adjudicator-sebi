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

## Phase 1 — Corpus & data model  ⏳ NEXT (awaiting spec sign-off)
Clean, structured, temporally-correct obligations + relations.
- Obligation schema, `obligation_relations` table (citation graph behind tool T4), temporal model,
  structure-aware clause chunking with parent links.
- ADR 1.1 narrow relations table vs GraphRAG vs graph DB; ADR 1.2 chunk grain.
- Gate: ≥ X% obligations have resolved temporal metadata; edges spot-check to source.

## Phase 2 — Ingestion pipeline
Fetch (curated seed) → parse → LLM-assisted extract (human-in-the-loop = gold seed) → extract
relations from appendix rescinded-lists → contextual enrichment → embed + index (pgvector + tsvector).
- Gate: extraction accuracy ≥ threshold; idempotent (re-run ≠ duplicates).

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
