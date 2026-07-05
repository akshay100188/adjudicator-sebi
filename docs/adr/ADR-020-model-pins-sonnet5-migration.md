# ADR-020: Model pins and the Sonnet 5 migration path

Status: accepted
Date: 2026-07-04
Plan ref: Phase 7 WI-3 · Swap deferred to WI-3b (guarded, gated)

## Context
The system pins three Claude models explicitly:
- Controller / agent — `claude-sonnet-4-6` (`backend/app/agent/agent.py:20`)
- Synthesis — `claude-sonnet-4-6` (`backend/app/synthesis/synthesize.py:22`)
- Reranker — `claude-haiku-4-5-20251001` (`backend/app/tools/rerank.py:16`)

`claude-sonnet-4-6` is a **real, currently-active model — nothing is broken and nothing is deprecated.**
The current Sonnet flagship is `claude-sonnet-5`, a drop-in successor. We record the migration as a
decision now so the path is understood; the actual swap is optional for v1 and lives in WI-3b.

## Options considered
- **Swap to `claude-sonnet-5` now** — newest flagship, better reasoning/synthesis. But it changes
  runtime behaviour (thinking, sampling, tokenizer) and must be re-validated against the eval suite
  before we can trust the finding P/R and citation-faithfulness numbers the writeup quotes.
- **Stay pinned on `claude-sonnet-4-6` for v1 (chosen)** — active, valid, already measured. The
  portfolio artifact's numbers (EXP-005, TRAJ-T01..04, WI-1) were all produced on 4-6; keeping the pin
  keeps the writeup's numbers reproducible with zero re-validation cost.

## Decision
**Stay pinned on `claude-sonnet-4-6` for v1 stability.** Capture the migration recipe here; execute it
in WI-3b when convenient, gated on a before/after guarded experiment (EXP-010).

### The swap (WI-3b)
Change the string `claude-sonnet-4-6` → `claude-sonnet-5` in `agent.py:20` and `synthesize.py:22`.
The reranker (`rerank.py`, Haiku) is out of scope for this migration.

### Three breaking changes to verify BEFORE swapping
1. **Adaptive thinking is on by default.** Sonnet 5 decides its own thinking depth; no config needed,
   but expect different latency/token profiles per call.
2. **Manual extended thinking is rejected.** `thinking: {type: "enabled", budget_tokens: N}` returns
   **HTTP 400**. Use the `effort` parameter instead. (Our current calls set no `thinking` block, so this
   is a "do not add it" note.)
3. **Non-default sampling params are rejected.** Passing `temperature` / `top_p` / `top_k` returns
   **HTTP 400** — they must be removed. Audit every `messages.create(...)` call before swapping.
   (Current calls in `agent.py`, `synthesize.py`, `rerank.py` pass only `max_tokens` — verified clean —
   but re-check at swap time.)

### Tokenizer change
Sonnet 5 uses a **new tokenizer: ~30% more tokens for the same text.** Recount tokens and revisit any
`max_tokens` sized close to expected output — notably `agent.py` (`max_tokens=1500` per loop step) and
the synthesis call — so a longer answer is not silently truncated.

## Why the others were rejected
Swapping now would invalidate the reproducibility of every number in the Phase 7 writeup until the eval
suite is re-run, for no v1 benefit — 4-6 is active, fast, and already measured. The learning rule
("no knob tuned without a metric") applies to the model pin too: a model swap is a knob, so it must be
run as a guarded before/after experiment, not a blind bump.

## Consequences / what we'll measure
- v1 ships on `claude-sonnet-4-6`; all quoted numbers trace to runs on that pin.
- **WI-3b, when run:** apply the three fixes + tokenizer/`max_tokens` recheck, then run the scenario
  eval + agent eval **before and after**; compare finding P/R, citation faithfulness, cost, and latency;
  **keep or revert on the numbers.** Log as EXP-010 and record the decision back here.
- 🚦 GATE (PO): run WI-3b now, or backlog it? **Recommendation: backlog** — 4-6 is active and fine.
