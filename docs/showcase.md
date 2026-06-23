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

## One-line version
> "I built an agentic RAG compliance prototype over public SEBI circulars, optimised against false
> negatives, evaluated on both answer and trajectory — and I can tell you exactly why I chose *not*
> to make it a product."
