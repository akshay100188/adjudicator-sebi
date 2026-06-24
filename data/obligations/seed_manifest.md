# v1 Seed Manifest — Stock Brokers (locked)

The bounded, version-controlled corpus boundary for v1 (ADR-001, ADR-008). Only **public** SEBI text,
non-commercial, never redistributed as a database (`docs/checklist.md`).

## Anchor (consolidated current position)
| Field | Value |
|---|---|
| Title | Master Circular for Stock Brokers |
| Circular ref | `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` |
| Issue date | 2024-08-09 |
| Source | https://www.sebi.gov.in/legal/master-circulars/aug-2024/master-circular-for-stock-brokers_85605.html |
| Supersedes | Master Circular for Stock Brokers dated 2024-05-22 |
| Relation seed | The May-2024 master's **Appendix** lists the individual circulars it rescinded → seeds `consolidated_by` / `supersedes` edges in `adj_obligation_relations` |

## v1 gold scope (the hand-reviewed, measured slice)
**Chapter:** Settlement of running account of client funds & securities (client-funds chapter).
- Richest amendment history → exercises multi-hop + `graph_lookup` + corrective retrieval.
- Matches the project's flagship example ("running-account settlement compliant as of today?").
- Other chapters of the master circular: ingested later as **non-gold context**, not hand-labelled in v1.

## Relation chain to capture (tool T4 graph)
```
base/amending circulars (running-account settlement, pre-2024)
        │  amends / supersedes
        ▼
Master Circular 2024-05-22  ──consolidated_by──►  (rescinds the base circulars)
        │  superseded_by
        ▼
Master Circular 2024-08-09 (SEBI/.../CIR/2024/110)  ← current valid position
```

## Ingestion plan (Phase 2, once API keys present)
1. Fetch the Aug-2024 master circular PDF + the May-2024 master circular PDF (for its Appendix).
2. Parse → isolate the running-account-settlement chapter; preserve clause/section structure.
3. Parse the May-2024 Appendix table → deterministic `adj_obligation_relations` edges (no LLM needed).
4. LLM-assisted obligation extraction on the chapter → **human review** (gold seed) — ADR-009.
5. Contextual-enrichment hook (`context_blurb`) — on/off decided in Phase 3 (ADR-010).
6. Embed (`text-embedding-3-small` @512) + index; populate `tsv`. Idempotent.

## Status — INGESTED ✅ (54 obligations across 5 chapters)

**Chapter 47 — Settlement of Running Account (fully human-reviewed gold).** 16 obligations
(SB-RUNACCT-001..016). Review: 9 verbatim; AP duties split (010/011), intimation split (012/013),
clause 47.10 split into exchange monitoring (015) + TM no-excess-retention (016).

**Provisional chapters (auto-extracted, light review; refine in Phase 6 gold pass).**
| Ch | Topic | Obligations | Source circular |
|---|---|---|---|
| 17 | Early Warning Mechanism (client-securities diversion) | 19 (SB-EWMDS-*) | — |
| 45 | Handling of Client's Securities | 11 (SB-CLTSEC-*) | 2019/75 + 2022/153 |
| 46 | Validation of Pay-In of Securities | 7 (SB-PAYINVAL-*) | 2022/119 |
| 48 | Risk disclosure for F&O traders | 4 (SB-RISKDISC-*) | 2023/73 |
| 92 | Bank Guarantees from client funds | 6 (SB-BGCF-*) | 2023/061 |
| 93 | Upstreaming of clients' funds | 14 (SB-UPSTREAM-*) | 2023/187 |

**Curated `refers_to` cross-edges (7):** obligation-level cross-references grounded in shared defined
terms — USCNBA (RUNACCT-003, UPSTREAM-013 → UPSTREAM-002), the client unpaid securities pledgee account
(CLTSEC-007/010/011 → CLTSEC-002), and MFOS (UPSTREAM-009/010 → UPSTREAM-008). Surfaced in
`expand_to_parent`, the obligation-detail API, and the UI. `scripts/seed_cross_refs.py`.

Cross-reference worth wiring as a `refers_to` edge: SB-RUNACCT-003 ↔ SB-UPSTREAM-002 (both the USCNBA).

**Phase 6 light review pass (provisional chapters):** titles verified complete (no truncation);
parser improved to capture the older `CIR/.../CIR/P/YYYY/NN` circular format and pair each ref with its
own date — this added ch45's previously-missed source circular `CIR/HO/MIRSD/DOP/CIR/P/2019/75`
(June 2019) and corrected its date pairing. Citation graph now **15 edges**.
Bundles: `review/chapter_{45,46,47,92,93}_bundle.json`. Total: 54 obligations, 15 edges, 54 chunks.
