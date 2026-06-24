# TRAJ-T03: What's the position on client money sitting in our account?

Route chosen: **multi-hop**  (gold: multi-hop)  
Correction fired: False  (gold expects: True)  
Steps: 4  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | hybrid_search | `{"query": "running account settlement of client funds", "top` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 2 | hybrid_search | `{"query": "upstreaming of client funds stock broker", "top_k` | {'results': [{'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client  |
| 3 | temporal_filter | `{"as_of": "2026-06-24"}` | {'as_of': '2026-06-24', 'valid_count': 54, 'valid_obligation_ids': '[54 ids]'} |
| 4 | rerank | `{"query": "client money held in broker account - settlement,` | {'reranked': [{'obligation_id': 'SB-UPSTREAM-001', 'title': '', 'score': 0.95},  |
| 5 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-001"}` | {'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client Clear Credit  |
| 6 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-016"}` | {'obligation_id': 'SB-RUNACCT-016', 'title': 'Do Not Retain Excess Client Funds  |
| 7 | graph_lookup | `{"circular_ref": "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110"}` | {'edges': [{'from_ref': 'SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110', 'to_ref': 'S |
| 8 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-002"}` | {'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated USCNBA for Re |
| 9 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-003"}` | {'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Received Post-Set |
| 10 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-003"}` | {'obligation_id': 'SB-UPSTREAM-003', 'title': 'Maintain Designated DSCNBA for Pa |
| 11 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-006"}` | {'obligation_id': 'SB-RUNACCT-006', 'title': "Settle Running Account Only via Ac |
| 12 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-009"}` | {'obligation_id': 'SB-RUNACCT-009', 'title': 'Discontinue Retention of Funds for |
| 13 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-013"}` | {'obligation_id': 'SB-UPSTREAM-013', 'title': 'Retain Unupstreamed Client Balanc |
| 14 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-005"}` | {'obligation_id': 'SB-UPSTREAM-005', 'title': 'Process Client Fund Release Reque |

Gold tools: `['hybrid_search', 'rerank', 'hybrid_search']`  
Actual tools: `['hybrid_search', 'hybrid_search', 'temporal_filter', 'rerank', 'expand_to_parent', 'expand_to_parent', 'graph_lookup', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent']`  
Key tool (rerank) hit: True

## Obligations returned
['SB-UPSTREAM-001', 'SB-UPSTREAM-002', 'SB-UPSTREAM-003', 'SB-UPSTREAM-005', 'SB-UPSTREAM-013', 'SB-RUNACCT-003', 'SB-RUNACCT-006', 'SB-RUNACCT-009', 'SB-RUNACCT-016']

## Reasoning
Client money held at the broker is governed by two interlocking frameworks, both now consolidated into master circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110 (which superseded 2024/53 and consolidated six prior circulars back to 2021). First, the Running Account Settlement framework (SB-RUNACCT-003, -006, -009, -016) prohibits retaining excess client funds after settlement, requires actual bank-account payment (not journal entries), bans retention on administrative-difficulty grounds, and mandates that post-settlement receipts be ring-fenced in the USCNBA. Second, the Upstreaming framework (SB-UPSTREAM-001, -002, -003, -005, -013) requires all client clear credit balances to be upstreamed to Clearing Corporations on an EOD basis (as cash, lien on FDRs, or pledge of MFOS units), all client inflows to be received only via the designated USCNBA, all outflows paid only from the DSCNBA, fund release requests processed by the next settlement day, and any late-received balances held in USCNBA until next-day upstreaming — effectively prohibiting any client money from sitting idle in a broker's general account.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
