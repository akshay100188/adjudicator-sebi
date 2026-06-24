# EXP-005: Synthesis precision — taming phantom gap findings

Date: 2026-06-24
Related ADR: ADR-017
Setup: full pipeline (agent → synthesis) over 6 gold scenarios (5 non-compliant + 1 compliant control)

## Hypothesis
The recall-first agent passes a broad obligation set to synthesis. If synthesis treats "obligation
applies but scenario is silent / actually complies" as a gap, precision collapses and a compliant
scenario yields phantom findings (the v1 failure mode).

## Change
Synthesis prompt: from "emit a finding when the scenario falls short" → a strict contradiction
contract: *emit only if the scenario contains a specific statement that directly CONTRADICTS the
obligation; evidence must be that statement; SILENCE IS NOT A GAP; COMPLIANCE IS NOT A GAP; a
good-practice scenario must return an empty array.*

## Metric before / after
| metric | before | after |
|---|---|---|
| finding precision | 0.34 | **0.65** |
| finding recall | 1.00 | **1.00** |
| citation faithfulness | 1.00 | **1.00** |
| compliant control (S06) → 0 findings | **FAIL** (10 findings) | **PASS** (0) |

## Analysis
- The single most important fix: the **compliant control now yields zero findings** — the
  anti-hallucination property the whole compliance framing depends on.
- Precision nearly doubled (0.34 → 0.65) while recall stayed at 1.00 (recall-first preserved).
- Remaining false positives (S03 +3, S04 +1, S05 +2) are largely **debatable-gold**, not fabrications:
  e.g. S03's "pooled client money" arguably does implicate upstreaming/segregation (UPSTREAM-001/002);
  S05 describes unpaid-securities handling that touches CLTSEC-002/005. These are candidates to ADD to
  the gold expected set, or genuinely borderline — a Phase 6 gold-refinement task, not a synthesis bug.
- Every emitted finding remained grounded (faithfulness 1.00) — the code-enforced grounding gate held.

## Verdict
**keep the contradiction contract.** Precision 0.65 / recall 1.00 / faithfulness 1.00, compliant
control passes. Next precision lever (future EXP): reconcile the debatable-gold scenarios, then
consider a Haiku pre-filter that drops obligations the scenario doesn't mention before Sonnet.
