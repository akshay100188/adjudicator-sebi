# EXP-007: Contextual Retrieval on/off (2026-07-05)

Related ADR: ADR-010 (contextual retrieval). Plan ref: WI-7.
Dense recall@k, 35 golden queries, 77 obligations, text-embedding-3-small@512. In-memory; production embeddings untouched.

## Hypothesis
Prepending an LLM blurb that situates each clause in its parent section lifts dense recall by disambiguating context-dependent clauses ("such person shall…").

## Sample blurb
> Stock Brokers and Clearing Members are prohibited from creating new Bank Guarantees using clients' funds to protect investor interests.

## Results (dense recall@k)
| config | recall@1 | recall@3 | recall@5 |
|---|---|---|---|
| contextual OFF (chunk only) | 0.74 | 0.93 | 1.00 |
| contextual ON (blurb + chunk) | 0.79 | 0.99 | 1.00 |
| **delta** | +0.04 | +0.06 | +0.00 |

## Analysis
- Contextual enrichment gives a **real, modest early-rank lift**: recall@1 **0.74 → 0.79**, recall@3
  **0.93 → 0.99**. The blurb disambiguates context-dependent clauses (the sample above turns a bare
  "shall not create bank guarantees" chunk into one that names *whose* funds and *who* is bound).
- **recall@5 is unchanged at 1.00** — the gold obligation was already in the top-5 dense pool without
  the blurb. As in the embedding bake-off (EXP-008), the reranked pipeline (pool 10 → Haiku → top-5)
  already delivers recall@1 0.91 / recall@3 1.00 on plain chunks, so it **already recovers** the
  early-rank recall the blurb would add.
- The baseline here (0.74 / 0.93 / 1.00) exactly matches EXP-008's `-3-small`@512 chunk-only run — a
  consistency check that the two experiments measured the same thing.

## Verdict
**Keep contextual retrieval OFF by default for v1; documented as a ready, positive-only lever.** The
lift is genuine but small and does not move the end-to-end number (recall@5 already 1.00; the reranker
already covers recall@1/@3). It never *hurts* recall (+0.00 at @5, positive at @1/@3) and is a one-time,
prompt-cacheable ingest cost — so it is the **first lever to switch on** if dense recall@5 starts
dropping below 1.00 as the corpus grows (the ADR-010 trigger), ahead of the heavier embedding-model
swap (EXP-008). No change to the v1 pipeline; ADR-010's "decide on the number" is now decided —
off for v1, on when scale erodes early-rank recall.

