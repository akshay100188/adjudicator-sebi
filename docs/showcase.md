# Showcase thesis — "why this is a prototype, not a product"

*(Draft — the most senior part of the story. Treated as a first-class deliverable.)*

The rarest signal an engineer can show is **knowing why you didn't ship.** Adjudicator is
deliberately a prototype. Three structural reasons make a commercial version a bad idea, and the
prototype framing neutralises all three.

## Why it can't ship commercially

1. **Liability.** A compliance tool that misses an obligation creates *regulatory risk for its user.*
   A false negative isn't a bug — it's a potential enforcement exposure for the customer. Carrying
   that liability requires insurance, legal review, and certification machinery a portfolio project
   has no business simulating.

2. **Content licensing.** Curated regulatory databases are a **defended, licensed market** (Thomson
   Reuters Regulatory Intelligence, Wolters Kluwer OneSumX). Redistributing a curated obligation
   database as a product walks into that. We use only **public** SEBI text and never ship the corpus
   as a standalone database.

3. **Entrenched incumbents.** The RegTech market is held by heavyweights with sales, compliance, and
   trust moats. Competing is not the goal; **demonstrating capability** is.

## How the prototype framing neutralises all three

- **Nothing relies on it for real decisions.** *Not legal advice / expert review only* on every
  finding (non-removable). → defuses liability.
- **Public text, non-commercial, never redistributed as a database.** → defuses licensing.
- **Capability demonstration, not a market entrant.** → no competitive exposure.

## What the prototype is actually demonstrating

The full modern RAG surface **plus the agentic control layer and how you evaluate it**:
- dense vs. sparse retrieval, RRF fusion, contextual enrichment, reranking, parent-document retrieval;
- an agent that routes, decomposes, traces supersession multi-hop, self-corrects on weak retrieval,
  and checks its own grounding before answering;
- and the part most portfolios skip — **trajectory evaluation**: judging the agent's *path*, not just
  its answer.

The interview-defensible artifact is the ADRs + experiment logs + golden dataset + the
**agent-trajectory viewer**.

## What was actually built (results on record)

A working, measured agentic RAG system over 54 real SEBI Stock-Broker obligations (5 chapters of the
Aug-2024 Master Circular), on an isolated Postgres schema.

| Layer | Result | Where |
|---|---|---|
| Corpus | 54 obligations, temporal model + 15-edge citation graph | ADR-001/006/007, seed_manifest |
| Retrieval | recall@5 **1.00**, MRR **0.97**; choices validated at 3× scale | EXP-001–004, ADR-011–014 |
| Agent (§7) | route **4/4**, key-tool **4/4**, grounding-clean **4/4** | ADR-016, TRAJ-T01–04 |
| Synthesis | finding recall **1.00**, precision **0.76**, faithfulness **1.00**, compliant control → 0 findings | EXP-005, ADR-017 |

The headline behaviour: on *"is our running-account settlement policy compliant today, and what
changed?"* the agent routes multi-hop, retrieves, and **traces the citation graph** — master
`2024/110` → supersedes `2024/53` → consolidates 6 circulars (2019–2023) — then confirms validity and
synthesises cited findings. A fixed pipeline would answer from the first hit and miss the chain.

The interview-defensible record: **18 ADRs** (every real decision), **6 experiment logs** (including a
genuine precision bug caught and fixed in EXP-005), **trajectory logs**, gold datasets, and a recall
regression gate. *No knob was tuned without a metric attached.*

## How to run

```
# backend (engine + API)
cd backend && pip install -r requirements.txt           # set backend/.env (Supabase + API keys)
uvicorn app.main:app --port 8001

# frontend (UI)
cd frontend && npm install && npm run dev               # http://localhost:3000
```
Eval anytime: `python eval/regression_gate.py` · `python scripts/run_agent_eval.py` ·
`python scripts/run_scenario_eval.py`.

## One-line version
> "I built an agentic RAG compliance prototype over public SEBI circulars, optimised against false
> negatives, evaluated on both answer and trajectory — and I can tell you exactly why I chose *not*
> to make it a product."
