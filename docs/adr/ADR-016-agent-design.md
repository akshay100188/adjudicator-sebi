# ADR-016: Agent design — bounded agency, fine tools, grounding gate

Status: accepted
Date: 2026-06-24
Plan ref: ADR 4.2 (bounded agency), ADR 4.3 (tool granularity); builds on ADR-002 (hand-rolled)

## Context
The hand-rolled ReAct controller (ADR-002) needs concrete design choices: how to bound it, how
granular the tools are, and how it avoids hallucinating obligations.

## Decisions
1. **Bounded agency (ADR 4.2).** Hard cap of `MAX_STEPS = 8` tool-call rounds. Unbounded agents are
   unevaluable and can rack up cost / loop. Every tool call is logged to a trajectory.
2. **Fine-grained tools (ADR 4.3).** Five distinct tools (temporal_filter, hybrid_search, rerank,
   expand_to_parent, graph_lookup) rather than one coarse `search`. Fine tools produce a *legible*
   trajectory — you can see the agent choose graph_lookup on a supersession question — which is exactly
   what makes the agentic claim measurable (§7 tool-selection accuracy).
3. **Grounding gate (Self-RAG).** The agent may only report obligation IDs that a tool actually
   returned this session. Enforced two ways: instructed in the system prompt AND filtered in code
   (`surfaced` set); any dropped IDs are recorded as `grounding_dropped`. This is the hallucination guard.
4. **Behaviours via prompt + tools** (not trained models): routing (simple vs multi-hop), query
   reformulation to canonical SEBI terms, multi-hop (hybrid→expand→graph_lookup→temporal_filter),
   corrective re-retrieval, and the grounding self-check.
5. **Controller = Sonnet**, structured JSON final output (route, relevant_obligations, reasoning,
   correction_fired) for evaluability and downstream synthesis (Phase 5).

## Why
A learning project's value is being able to explain and *measure* the loop. Bounding + fine tools +
a code-enforced grounding gate make the agent inspectable, cheap-bounded, and safe against fabricated
citations — the three things that matter for both the showcase and the compliance framing.

## Consequences / what we'll measure
- Agent eval (`scripts/run_agent_eval.py`, §7): route accuracy, key-tool hit, tool-set overlap,
  correction correctness, grounding-clean rate. TRAJ logs written to `docs/trajectories/`.
- Watch avg steps / cost; tighten MAX_STEPS or tool descriptions if the agent over-expands.

## Correction-trigger reliability (measured, 2026-07-05)
A repeated-run probe (`scripts/probe_correction_variance.py`, 3 reps × 4 gold trajectories) isolates the
one stochastic axis, corrective re-retrieval (CRAG):
- **Specificity is perfect:** on the 3 queries that should NOT trigger correction (T01/T02/T04), it
  fired **0/9** — it never over-corrects.
- **Sensitivity is weak:** on the one query that SHOULD trigger a canonical-terminology reformulation
  (T03, "client money" → running-account settlement / upstreaming), it fired only **1/3** in the probe
  (and 0/1 in the initial eval run) — roughly **1 in 4**.
This was a **real limitation, not run-to-run noise**: the corrective behaviour is correct *when* it
fires, but its trigger was under-sensitive on lay-phrasing queries. Route/key-tool/grounding are stable
at 4/4.

## Correction-trigger fix (EXP-011, 2026-07-06)
Diagnosed as a **trigger/decision failure, not a capability failure** — the agent *can* reformulate lay
phrasing; it failed to *recognise when to*. Two fixes were considered:
- **Fix A (rejected, measured):** trigger correction off an objective rerank top-1 score below a
  threshold. WI-3 feasibility probe killed it — correction-expecting queries score 0.80–0.90 (the
  reranker is confidently wrong), fully overlapping the clean 0.85–1.00 range; **no separating
  threshold exists**.
- **Fix B (chosen):** replace the fuzzy "results look weak" self-judgment with a **forced structured
  self-check** — after the first `hybrid_search` the agent must explicitly state whether the top result
  directly addresses the specific concept, and a "no"/lay-phrasing **mandates** reformulation.
  Implemented as `CORRECTION_CLAUSES` / `run_agent(correction_strictness=…)`, kept general (no
  gold-query-specific mappings, so it isn't tuned to the test).

Swept strictness 0/1/2 on an expanded gold set (**N = 5 correction-expecting + 6 not-expecting**, 3 reps):
sensitivity 0.00 / 0.53 / 0.87 against specificity 1.00 / 0.81 / 0.72 — a **monotonic trade-off; no level
holds specificity at 1.00 while raising sensitivity**. **Operating point (PO): Level 1** — sensitivity
**0.00 → 0.53**, specificity **1.00 → 0.81** (loss entirely on one borderline query, T04). This is a
**scoped, demonstration-scale** improvement (N small, stated), not population-level reliability. Residual:
the widest lay↔canonical gaps (e.g. "earn interest on client money" → MFOS) still under-fire even at L2.
See EXP-011 for the full sweep. `CORRECTION_STRICTNESS = 1` in `agent.py`.
