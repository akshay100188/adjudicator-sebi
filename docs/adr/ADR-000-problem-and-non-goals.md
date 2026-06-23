# ADR-000: Problem statement, scope, and non-goals

Status: accepted
Date: 2026-06-23

## Context
Before any code, fix what "success" means and — equally important — what we refuse to build. This
project is a **learning artifact and portfolio piece**, not a commercial product. The architecture
is **agentic RAG** over the public SEBI corpus. This ADR is the anchor every later ADR refers back to.

## The problem
Given an unstructured input (a product-change **scenario**, later an uploaded **document**), an LLM
**agent** must retrieve the **currently-valid** SEBI obligations that apply, trace supersession and
cross-references to reach the *consolidated* position, and surface where the input falls short — with
**every finding cited back to a source circular**.

The worst failure mode, and the one we optimise against, is a **false negative**: a real obligation
that is never retrieved → a silent compliance gap. Hence retrieval is **recall-first** (§6).

## Why agentic (not a fixed pipeline)
SEBI questions are genuinely multi-step. *"Is our running-account settlement policy compliant as of
today?"* requires: find the base circular → trace its amendments → check whether a master circular
consolidated it → confirm nothing later superseded it → synthesise with citations. A fixed pipeline
answers from whatever one retrieval returned and can miss the amendment. An agent **follows the
chain**. The hybrid retrieval stack does not disappear — it becomes the **toolbox the agent calls**.

## In scope (v1)
1. A bounded SEBI **obligation corpus** (Stock Brokers family) with temporal/supersession metadata.
2. The **retrieval substrate** (hybrid + contextual + narrow citation graph) exposed as **agent tools**.
3. The **agent**: routing, decomposition, multi-hop, corrective retrieval, grounded synthesis.
4. **Gap-detection** output — structured **scenarios** first (document upload later, ADR-003).
5. An **eval harness** with a golden dataset **and trajectory evaluation**.
6. A minimal **interface** + the showcase writeup.

## Non-goals (deliberate refusals)
- Not all of SEBI — one family for v1 (ADR-001).
- Not multi-jurisdiction. Engine is domain-agnostic; the demo corpus is SEBI only.
- **Not legal advice or certification.** Disclaimer on every finding: *for expert review only.*
- Not real-time regulatory monitoring (no RSS-watcher in v1).
- **Not full GraphRAG.** A narrow citation graph is a tool, not the architecture (ADR-001-graph TBD Phase 1).
- Code-analysis is a **stretch** (Phase 8), not core (ADR-005). It must not eat the RAG/agent learning.

## Decision
Build v2 as agentic RAG, recall-first, with the scope/non-goals above, in a **clean-slate repo**
(`adjudicator-sebi`) separate from the v1 fixed-pipeline product.

## Why a clean slate (vs. extending v1)
The v1 codebase is a multi-jurisdiction fixed-pipeline product whose schema has **no temporal or
relations model** and whose engine hard-codes the control flow. The v2 correctness backbone is
temporal validity + typed supersession edges + an agent loop — all of which fight v1's design.
Starting fresh keeps the learning artifact clean and the mental model honest; reusing v1 plumbing
would import baggage we'd spend more time removing than rebuilding.

## Consequences / what we'll measure
Every later phase is gated on a metric in `docs/metrics.md`. Phase gates are non-negotiable: no
building past an unsigned gate. The interview-defensible record is the set of ADRs, experiment logs,
trajectory logs, and the golden dataset.
