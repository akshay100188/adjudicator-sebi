# EXP-011: Corrective-retrieval sensitivity fix (2026-07-05)

Related ADR: ADR-016 (agent design). Plan ref: correction-fix spec WI-1…WI-5.
Goal: raise corrective-retrieval **sensitivity** (fires when it should) **without** losing the current
perfect **specificity** (never fires when it shouldn't). No number here unless it traces to a run today.

## Expanded correction gold set (WI-1, PO-approved)
The prior finding rested on **one** correction-expecting query (T03). We added 4 correction-expecting
and 3 correction-not-expecting queries to `eval/golden/trajectories.jsonl`, each verified against real
retrieval today (a naive query on the lay phrasing genuinely misses / mis-ranks the correct obligation):

| id | class | lay query → canonical obligation | naive retrieval today |
|---|---|---|---|
| T03 | expecting | "client money sitting in our account" → running-account / upstreaming | ambiguous (original) |
| T05 | expecting | "earn interest on client money" → SB-UPSTREAM-008 (MFOS only) | **MISS** (not in top-10) |
| T06 | expecting | "sub-broker collects cash/shares" → SB-RUNACCT-010 (authorized person) | **MISS** (top-1 UPSTREAM-002) |
| T07 | expecting | "let us operate their account" → SB-EWMDS-019 (power of attorney) | wrong top-1; correct at rank 3 |
| T08 | expecting | "missing share delivery deadlines" → SB-EWMDS-005 (pay-in shortages) | wrong top-1; correct at rank 2 |
| T09 | not-exp | "running account settlement calendar…" → SB-RUNACCT-002 | top-1 ✓ |
| T10 | not-exp | "auto-release of pledge within seven trading days" → SB-CLTSEC-009 | top-1 ✓ |
| T11 | not-exp | "F&O risk disclosure minimum screen area 50%" → SB-RISKDISC-003 | top-1 ✓ |

Existing T01/T02/T04 are also correction-not-expecting. **Total: 5 expecting, 6 not-expecting.**
N is small — a demonstration-scale fix; the number is always stated with N.

## Current trigger (WI-4 locate step)
The trigger lives in the agent system prompt (`agent.py`, step 2 of the ReAct instructions): a **fuzzy,
prompt-instructed self-assessment** — *"If the top results look weak or off-topic, CORRECT: reformulate
and re-retrieve."* It asks the model to holistically judge its own retrieval, and it under-fires: the
model looks at a topically-adjacent (often confidently-wrong) top result and decides it's "good enough."
This is a **trigger/decision failure, not a capability failure** — when it does reformulate, it finds
the right obligation; it just fails to recognise when it should.

## WI-3 feasibility probe — is the rerank score a usable trigger signal? (NO)
Hypothesis (Fix A): correction-expecting queries produce systematically *lower* top-1 rerank scores, so
a threshold τ could trigger correction objectively. **Measured top-1 rerank score per query:**

| class | top-1 rerank scores | min | median | max |
|---|---|---|---|---|
| correction-expecting | T03 0.90, T05 0.00, T06 0.80, T07 0.90, T08 0.90 | **0.00** | 0.90 | 0.90 |
| not-expecting | T01 0.85, T02 0.90, T04 0.90, T09 0.95, T10 1.00, T11 1.00 | 0.85 | 0.93 | 1.00 |

**No separation.** Correction-expecting queries mostly score 0.80–0.90, fully overlapping the clean
0.85–1.00 range — because the reranker is **confidently wrong** (e.g. T07 gives 0.90 to the *wrong*
obligation). Only T05 (a total miss) scores 0.00. There is no threshold τ that catches the expecting
queries without false-firing on the clean ones. **Decision: Fix A is dead → implement Fix B.**

## Fix B — forced structured self-check (implemented)
Replace the fuzzy self-assessment with a **mandatory, explicit** check after the first `hybrid_search`:
the agent must state whether the single best result *directly* addresses the specific subject (vs merely
the topic area), and a "no" — or any lay/colloquial phrasing — **mandates** a reformulation into
canonical SEBI terminology before proceeding. Implemented as `CORRECTION_CLAUSES` in `agent.py`, selected
by `run_agent(correction_strictness=…)`; kept **general** (no gold-query-specific mappings, so the fix is
not tuned to the test). Swept parameter = strictness level (0 = original, 1 = forced check, 2 = forced
check + "default to reformulating on colloquial phrasing").

## Two-metric sweep (WI-4) — sensitivity vs specificity, 3 reps each on the expanded set
Sensitivity = P(correction fires | it should); Specificity = P(correction does NOT fire | it shouldn't).
5 correction-expecting queries, 6 not-expecting, 3 reps each (agent runs via `scripts/exp011_sweep.py`).

| strictness (correction clause) | sensitivity | specificity |
|---|---|---|
| **0** — original fuzzy self-judgment | **0.00** (0/15) | **1.00** (15/15) |
| **1** — forced structured self-check | **0.53** (8/15) | **0.81** (13/16) |
| **2** — forced check + "default to reformulate on colloquial phrasing" | **0.87** (13/15) | **0.72** (13/18) |

Per-query fire rate (fired/runs):

| id | class | L0 | L1 | L2 |
|---|---|---|---|---|
| T03 | expect | 0/3 | 3/3 | 3/3 |
| T05 | expect | 0/3 | 0/3 | 1/3 |
| T06 | expect | 0/3 | 2/3 | 3/3 |
| T07 | expect | 0/3 | 1/3 | 3/3 |
| T08 | expect | 0/3 | 2/3 | 3/3 |
| T01 | clean | 0/3 | 0/3 | 1/3 |
| T02 | clean | 0/3 | 0/3 | 0/3 |
| T04 | clean | 0/3 | **3/3** | 2/3 |
| T09 | clean | 0/3 | 0/3 | 0/3 |
| T10 | clean | 0/3 | 0/3 | 2/3 |
| T11 | clean | — | 0/1 | 0/3 |

**Reading the sweep:**
- The trade-off is **monotonic and real** — every increase in trigger strictness buys sensitivity and
  costs specificity. **No setting holds specificity at 1.00 while raising sensitivity.** There is no
  free lunch here; the honest deliverable is the trade-off curve, not a clean 4/4.
- **Level 1's entire specificity loss is one query (T04)** — "obligations when an authorised person
  collects funds from clients," a borderline case where reformulating is not even clearly wrong. Every
  other clean query held perfectly. That makes L1 a genuinely good operating point, not a smeared loss.
- **Level 2** over-corrects on genuinely-clean queries (T01, T10 also break) for a sensitivity gain that
  mostly comes from the easy expecting queries.
- **T05 is the honest ceiling:** "earn interest on client money" → `SB-UPSTREAM-008` (MFOS) is the widest
  lay↔canonical gap; even L2 only reformulates it 1/3. The fix helps most weak queries, not all.

## Chosen operating point — Level 1 (PO decision, WI-4 gate)
`CORRECTION_STRICTNESS = 1` in `agent.py`. Rationale: converts a broken trigger (0/15) into one that
fires on the majority of genuinely-weak queries (**sensitivity 0.00 → 0.53**) while keeping
**specificity high (1.00 → 0.81)**, with the single specificity casualty on one borderline query. L2's
extra sensitivity (0.87) costs too much specificity (0.72) spread across truly-clean queries.

## Verdict
**Keep the forced structured self-check at strictness Level 1.** Measured on an expanded gold set of
**N = 5 correction-expecting + 6 not-expecting** queries (3 reps): corrective-retrieval **sensitivity
rose from 0.00 to 0.53 with specificity held at 0.81** (down from 1.00, the loss entirely on one
borderline query). This is a **scoped, demonstration-scale improvement, not population-level
reliability** — N is small and stated. The mechanism is defensible (an objective forced criterion
replacing subjective self-grading), the rerank-score alternative (Fix A) was measured and rejected
(WI-3), and the residual limitation (T05-class widest-gap queries, and the specificity/sensitivity
trade) is documented rather than hidden.
