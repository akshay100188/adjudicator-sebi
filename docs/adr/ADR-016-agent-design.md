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
This is a **real limitation, not run-to-run noise**: the corrective behaviour is correct *when* it
fires, but its trigger is under-sensitive on lay-phrasing queries. Route/key-tool/grounding are stable
at 4/4. Fix path (future): strengthen the CRAG trigger in the system prompt (an explicit low-confidence/
lay-phrasing check) and re-probe — do not claim "correction works reliably" until the sensitivity number
moves. Reported honestly in the showcase rather than rounded up.
