# EXP-006: Synthesis precision pass — second-pass adjudication (2026-07-05)

Related ADR: ADR-017 (grounded synthesis). Plan ref: WI-A.
Full pipeline (agent -> synthesis) over 6 gold scenarios (5 non-compliant + 1 compliant control). Shared agent + first-pass; before = raw findings, after = adjudicated.

## Hypothesis
A strict per-finding second pass drops 'merely topically related' false positives (the EXP-005 residual at precision 0.76) while holding recall at 1.00.

## Metric before / after
| metric | before (raw) | after (adjudicated) |
|---|---|---|
| finding precision | 0.72 | 0.87 |
| finding recall | 1.00 | 1.00 |
| citation faithfulness | 1.00 | 1.00 |
| S06 compliant control -> 0 findings | PASS | PASS |

## Rejected findings (auditable drop log)
| scenario | dropped obligation | correct drop? | reason |
|---|---|---|---|
| S01 | SB-RUNACCT-016 | yes | The violation requires inferring that retained funds are 'excess' and retained specifically 'as on the date of settlement,' neither of which is stated; the core retention-for-operational-reasons violation is already captured by SB-RUNACCT-009. |
| S03 | SB-EWMDS-010 | yes | The obligation specifically concerns pledging of client securities with credit balances to raise funds, which is not what the scenario describes; the misuse of pooled client money for proprietary trades is already directly captured by SB-RUNACCT-011, and applying SB-EWMDS-010 here requires inference/analogy rather than a direct violation of its stated requirement. |
| S05 | SB-EWMDS-010 | yes | The violation is inferred — the scenario does not state that the pledged securities belong to clients with a credit balance; the same prohibited pledging practice is already captured more directly by SB-CLTSEC-011. |

## Analysis
- **Precision 0.72 → 0.87 with recall held at 1.00.** The second pass removed the exact failure mode
  EXP-005 flagged — "merely topically related" obligations the first, recall-first pass over-flags.
- **All 3 drops were correct.** Each removed obligation was a false positive (not in the gold expected
  set), and in every case the underlying real violation was **already captured by a more directly-
  evidenced finding** (S01: RUNACCT-009 already covers the retention; S03: RUNACCT-011 already covers
  the prop-trading misuse; S05: CLTSEC-011 already covers the pledging). **Zero true gaps were dropped**
  — recall stayed 1.00, the hard constraint.
- **The compliant control (S06) still yields zero findings** before and after — the anti-hallucination
  property is preserved; the precision pass only ever *removes*, so it cannot manufacture a gap.
- **Faithfulness stays 1.00** — every surviving finding remains grounded in a considered obligation.
- The drop log is emitted in the pipeline output as `rejected_findings` (with a one-clause reason each),
  so the precision decision is **auditable, not asserted** — you can see exactly what was dropped and why.

## Verdict
**Keep the second-pass adjudication (default on).** It lifts finding precision **0.72 → 0.87** while
holding recall at **1.00**, faithfulness at **1.00**, and the S06 compliant control at **0 findings** —
the WI-A gate passes cleanly, no recall/precision trade needed. Implemented as `adjudicate()` in
`synthesis/synthesize.py`, wired into `analyze_scenario(adjudicate_pass=True)`, with a fail-safe that
KEEPS any finding the adjudicator returns no verdict for (protecting recall). Note: synthesis is mildly
nondeterministic (~±0.05 run-to-run), so precision fluctuates around the reported figure; recall and the
S06 control are the invariants that must hold every run.

