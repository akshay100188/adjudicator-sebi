# ADR-017: Grounded synthesis — structured output, anti-hallucination, model split

Status: accepted
Date: 2026-06-24
Plan ref: ADR 5.1 (structured output), 5.2 (grounding), 5.3 (Haiku/Sonnet split)

## Context
Turn the agent's gathered obligations + the input scenario into compliance findings. Must be
evaluable, must not fabricate obligations, and must not invent gaps on compliant input.

## Decisions
1. **Structured output (ADR 5.1).** Findings are a JSON array of
   `{obligation_id, gap_summary, evidence, recommended_action, confidence}`; the citation is attached
   in *code* from the obligation's real `source_circular_ref` + clause refs (never from the LLM).
   Structured for evaluability (finding P/R) and a clean UI.
2. **Grounding / anti-hallucination (ADR 5.2).** Two gates: (a) the prompt forbids citing anything not
   in the provided obligation set; (b) code drops any finding whose `obligation_id` isn't in the set.
   Citations are derived from the DB, so a cited circular always actually backs the obligation.
3. **No phantom findings on compliant input.** The prompt emits a finding ONLY on a clear gap; silence
   otherwise. This encodes the v1 lesson (no fallback that invents gaps). The gold set includes a
   COMPLIANT control scenario (S06) that must produce zero findings.
4. **Model split (ADR 5.3).** Haiku does the cheap high-volume work (applicability/rerank inside the
   agent); Sonnet only does final finding generation on the survivor obligation set. Prompt caching on
   the system block.

## Why
Compliance output that fabricates an obligation or a citation is worse than useless — it manufactures
false risk. Code-enforced grounding + DB-derived citations + a compliant control scenario make the
faithfulness claim measurable, not aspirational.

## Consequences / what we'll measure
- `backend/app/synthesis/synthesize.py`; pipeline `analyze_scenario()`.
- Phase 5 metric (`scripts/run_scenario_eval.py`): finding precision/recall vs gold, citation
  faithfulness, and the compliant-control (zero findings) check.
- Every output carries the non-removable disclaimer.

## Update (EXP-006, WI-A) — second-pass adjudication for precision
Added a strict **second-pass adjudication** (`adjudicate()` in `synthesize.py`, on by default via
`analyze_scenario(adjudicate_pass=True)`). The first pass is recall-first and over-flags; the second
re-examines each proposed finding in isolation and drops "merely topically related" false positives
(the EXP-005 residual). It can only DROP, never add, so it cannot introduce a hallucination, and a
fail-safe keeps any finding it returns no verdict for (protecting recall). Dropped candidates are
surfaced as `rejected_findings` (with a reason) so the precision decision is auditable.
**Measured (EXP-006, current corpus):** finding precision **0.72 → 0.87**, recall **held at 1.00**,
faithfulness **1.00**, S06 compliant control **0 findings** — all 3 drops correct (no true gap lost).
