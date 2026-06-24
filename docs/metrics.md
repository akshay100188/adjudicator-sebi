# Success Metrics & Agent Evaluation

Defined **before** building; measured at every gate. The learning rule: no knob is tuned without a
metric attached.

## §6 — Success metrics

### Retrieval (Phase 3) — recall-first
In compliance the worst failure is a **false negative** (a real obligation never retrieved → silent
gap). So:
- **recall@k** — *primary.* Push aggressively. (Threshold set in Phase 3 spec.)
- **precision@k** — secondary (rerank + agent clean up).
- **nDCG / MRR** — ranking quality, used for tuning fusion.

### Gap detection (Phase 5)
- **Finding precision / recall** vs. gold.
- **Citation faithfulness** — % of findings whose cited circular actually supports the claim.

### Corpus health (Phase 1–2)
- % obligations with valid temporal metadata.
- Extraction accuracy vs. hand-labelled sample.
- Relation-edge accuracy (amends / supersedes / refers_to / consolidated_by).

### Operational
- Cost/run (₹/USD) — proves Haiku/Sonnet tiering + prompt caching.
- Latency/run.
- **Agent steps/run** — efficiency of the loop.

## §7 — Evaluating an agent (path, not just answer)

A fixed pipeline is judged on its *answer*. An agent must also be judged on its *path*.

### Outcome metrics
Right obligations + faithful citations (recall@k, finding P/R, faithfulness — above).

### Trajectory / process metrics
- **Tool-selection accuracy** — did it call the right tools? (e.g. `graph_lookup` on a supersession Q.)
- **Trajectory match** — closeness of tool sequence to the gold trajectory (exact-match or
  order-agnostic set overlap).
- **Corrective-trigger correctness** — did CRAG fire when (and only when) retrieval was weak?
- **Step efficiency** — answer quality per step; penalise looping / over-retrieval.
- **Grounding-gate precision** — did the Self-RAG check correctly block unsupported findings?

### RAGAS-style metrics (RAG layer)
faithfulness · answer relevance · context precision · context recall.

### LLM-as-judge
Fast and scalable for finding quality, but biased (verbosity / position bias). Always anchor against
a human-labelled slice.

### Tooling (pick one tracer + one metric suite, defend the choice)
Tracing: LangSmith / Arize Phoenix. Metric suites: RAGAS / DeepEval / TruLens.

## Metric gates by phase (filled as phases are specced)
| Phase | Gate metric | Threshold |
|---|---|---|
| 1 | % obligations with resolved temporal metadata | **100%** ✅ (hand-reviewed) |
| 1 | recursive supersession traversal correctness | pass ✅ |
| 2 | extraction faithfulness vs. human review | **high** ✅ (9/13 accepted verbatim; 4 split/reframed, content faithful) |
| 2 | idempotent ingest (re-run ≠ duplicates) | **PASS** ✅ (16/9/16 stable on re-run) |
| 3 | recall@5 golden set (35 q, 54 obligations) | **1.00** ✅ (hybrid+rerank); MRR **0.97** |
| 3 | retriever choice | hybrid+rerank (EXP-001), RRF k=60 (EXP-002), pool=10 (EXP-003) |
| 3 | choices hold at 3× corpus scale | **validated** ✅ (EXP-004): sparse degrades, rerank's lift grows |
| 4 | trajectory: route / key-tool / grounding | **4/4 · 4/4 · 4/4** ✅ (correction 3/4) |
| 5 | finding recall / precision | **1.00 / 0.76** ✅ (EXP-005, after gold reconciliation) |
| 5 | citation faithfulness; compliant control → 0 findings | **1.00 ✅ · PASS ✅** |
| 6 | harness reproduces a phase's numbers on demand | pass/fail |
