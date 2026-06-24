# Project Adjudicator (SEBI) — Agentic RAG

A regulatory-intelligence **prototype** over the public SEBI corpus, built as an **agentic RAG**
system. This is a **learning artifact and portfolio piece** — explicitly **not** a production
product, and explicitly **not** legal advice.

> Given an unstructured input (a product-change *scenario* or, later, an uploaded *policy
> document*), an LLM agent retrieves the set of **currently-valid** SEBI obligations that apply,
> traces supersession and cross-references to get the *consolidated* position, and surfaces where
> the input falls short — every finding cited back to a source circular.

## Why this is a prototype, not a product

See [`docs/showcase.md`](docs/showcase.md). In short: **liability** (a tool that misses an
obligation creates regulatory risk), **content licensing** (curated regulatory databases are a
defended market), and **entrenched incumbents**. The prototype framing neutralises all three:
nothing relies on it for real decisions, it uses only **public** SEBI text **non-commercially**,
and it demonstrates capability rather than competing.

**Every finding carries a non-removable disclaimer:** *for expert review only; not legal advice.*

## v1 scope (locked decisions)

| Decision | Choice | ADR |
|---|---|---|
| A — Corpus boundary | **Stock Brokers** family | [ADR-001](docs/adr/ADR-001-corpus-boundary.md) |
| B — Input modes | **Scenario-only first** (document upload later) | [ADR-003](docs/adr/ADR-003-input-modes.md) |
| C — Agent framework | **Hand-rolled Anthropic SDK tool-loop** | [ADR-002](docs/adr/ADR-002-agent-framework.md) |
| D — Embedding model | `text-embedding-3-small` @512 (benchmark in Phase 3) | [ADR-004](docs/adr/ADR-004-embedding-model.md) |
| E — Code module | **Out of v1** (Phase 8 stretch) | [ADR-005](docs/adr/ADR-005-code-module-scope.md) |

## Architecture (agentic)

An **agent controller** (Claude Sonnet, ReAct loop) decides per-step what to retrieve, calls a
**toolbox** of retrieval functions, self-corrects on weak retrieval, and checks its own grounding
before answering. The hybrid retrieval stack is the **substrate the agent calls as tools**.

```
INPUT → AGENT CONTROLLER (ReAct: Thought→Action→Observation)
          calls tools ↓
   T1 temporal_filter(date, family)   — valid obligations only (deterministic SQL)
   T2 hybrid_search(query, k)         — dense (pgvector) ⊕ BM25, fused with RRF
   T3 expand_to_parent(chunk_id)      — clause → parent section
   T4 graph_lookup(circular_ref)      — amends / supersedes / refers_to edges
   T5 rerank(query, candidates)       — Haiku / cross-encoder
          grounded evidence ↓
   SYNTHESIS (Sonnet, prompt-cached)  — structured cited findings
          ↓
   PERSIST finding metadata + trajectory log + human-review queue
```

## The interview-defensible record

- [`docs/adr/`](docs/adr/) — one ADR per real decision (options, choice, why others rejected, metric).
- [`docs/experiments/`](docs/experiments/) — every knob change with before/after metric.
- [`docs/trajectories/`](docs/trajectories/) — what the agent *decided to do*, not just what it answered.
- [`docs/metrics.md`](docs/metrics.md) — success metrics (§6) + how you evaluate an agent (§7).
- Golden dataset (from Phase 2 review) — gold queries, scenarios, and **gold trajectories**.

**The learning rule:** no knob gets tuned without a metric attached.

## Build status

See [`docs/build-plan.md`](docs/build-plan.md) for the phased plan.

| Phase | What | Status |
|---|---|---|
| 0 | Foundations & framing | ✅ |
| 1 | Corpus & data model (schema + relations + temporal) | ✅ |
| 2 | Ingestion pipeline (54 obligations, 5 chapters) | ✅ |
| 3 | Retrieval substrate (the agent's tools) — recall@5 1.00 | ✅ |
| 6 | Eval harness + regression gate (built early) | ✅ |
| 4 | The agent (ReAct; route/key-tool/grounding 4/4) | ✅ |
| 5 | Gap-detection / grounded synthesis (recall 1.00, precision 0.76) | ✅ |
| 7 | Interface & showcase (FastAPI + Next.js) | ✅ |
| 8 | Code-analysis module (stretch) | ⏳ out of v1 |

See [`docs/showcase.md`](docs/showcase.md) for the results table and run instructions.

## Stack

FastAPI · Supabase (Postgres + pgvector + tsvector) · OpenAI `text-embedding-3-small` ·
Claude Sonnet (controller + synthesis) + Haiku (scoring/rerank) · Next.js + Tailwind + shadcn/ui.

## Status: not legal advice

This system does not certify compliance. It identifies *potential* gaps for expert review and
links every finding to a source obligation. It must not be relied on for real compliance decisions.
