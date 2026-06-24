# TRAJ-T01: Is our running-account settlement policy compliant as of today, and has anything changed in the underlying rules?

Route chosen: **multi-hop**  (gold: multi-hop)  
Correction fired: False  (gold expects: False)  
Steps: 6  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | temporal_filter | `{"as_of": "2026-06-24"}` | {'as_of': '2026-06-24', 'valid_count': 54, 'valid_obligation_ids': '[54 ids]'} |
| 2 | hybrid_search | `{"query": "running account settlement of client funds", "top` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 3 | hybrid_search | `{"query": "upstreaming of client funds stock broker obligati` | {'results': [{'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client  |
| 4 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-001"}` | {'obligation_id': 'SB-RUNACCT-001', 'title': 'Settle Running Account on Exchange |
| 5 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-001"}` | {'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client Clear Credit  |
| 6 | hybrid_search | `{"query": "running account settlement frequency 30 days 90 d` | {'results': [{'obligation_id': 'SB-RUNACCT-006', 'title': "Settle Running Accoun |
| 7 | graph_lookup | `{"circular_ref": "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110"}` | {'edges': [{'from_ref': 'SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110', 'to_ref': 'S |
| 8 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-004"}` | {'obligation_id': 'SB-RUNACCT-004', 'title': 'Retain Only Permissible Funds for  |
| 9 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-016"}` | {'obligation_id': 'SB-RUNACCT-016', 'title': 'Do Not Retain Excess Client Funds  |
| 10 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-009"}` | {'obligation_id': 'SB-RUNACCT-009', 'title': 'Discontinue Retention of Funds for |
| 11 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-012"}` | {'obligation_id': 'SB-RUNACCT-012', 'title': 'Send SMS and Email Settlement Inti |
| 12 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-013"}` | {'obligation_id': 'SB-RUNACCT-013', 'title': 'Send Retention Statement with Runn |
| 13 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-005"}` | {'obligation_id': 'SB-UPSTREAM-005', 'title': 'Process Client Fund Release Reque |
| 14 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-013"}` | {'obligation_id': 'SB-UPSTREAM-013', 'title': 'Retain Unupstreamed Client Balanc |
| 15 | rerank | `{"query": "running account settlement policy obligations: fr` | {'reranked': [{'obligation_id': 'SB-RUNACCT-001', 'title': '', 'score': 0.95}, { |
| 16 | rerank | `{"query": "running account settlement client funds retention` | {'reranked': [{'obligation_id': 'SB-UPSTREAM-001', 'title': '', 'score': 0.9}, { |

Gold tools: `['temporal_filter', 'hybrid_search', 'graph_lookup', 'temporal_filter', 'rerank']`  
Actual tools: `['temporal_filter', 'hybrid_search', 'hybrid_search', 'expand_to_parent', 'expand_to_parent', 'hybrid_search', 'graph_lookup', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'rerank', 'rerank']`  
Key tool (graph_lookup) hit: True

## Obligations returned
['SB-RUNACCT-001', 'SB-RUNACCT-004', 'SB-RUNACCT-005', 'SB-RUNACCT-006', 'SB-RUNACCT-007', 'SB-RUNACCT-008', 'SB-RUNACCT-009', 'SB-RUNACCT-012', 'SB-RUNACCT-013', 'SB-RUNACCT-014', 'SB-RUNACCT-015', 'SB-RUNACCT-016', 'SB-UPSTREAM-001', 'SB-UPSTREAM-002', 'SB-UPSTREAM-003', 'SB-UPSTREAM-005', 'SB-UPSTREAM-013']

## Reasoning
All 17 obligations are confirmed valid as of 2026-06-24 (temporal_filter: 54 live obligations). They all source from the current master circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110. The graph_lookup shows this circular (a) supersedes the interim circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/53, and (b) consolidates six earlier circulars spanning 2021–2023 (CIR/2021/577, CIR/2022/101, CIR/2022/119, CIR/2022/153, CIR/2023/061, CIR/2023/187, CIR/2023/197) — meaning any policy built on those older circulars must be reviewed against the 2024 master. The obligations cover: settlement frequency and exchange-stipulated dates (SB-RUNACCT-001), permissible fund retention for outstanding positions (SB-RUNACCT-004/005), prohibition on excess retention (SB-RUNACCT-016), no administrative-difficulty exceptions for active clients (SB-RUNACCT-009), settlement only via direct bank payment (SB-RUNACCT-006), three-day return for inactive clients (SB-RUNACCT-007), date-of-realisation rule for physical instruments (SB-RUNACCT-008), SMS/email intimation (SB-RUNACCT-012), 5-working-day retention statement (SB-RUNACCT-013), 30-working-day client dispute window (SB-RUNACCT-014), exchange monitoring system (SB-RUNACCT-015), EOD upstreaming of all clear credit balances to CCs (SB-UPSTREAM-001), designated USCNBA/DSCNBA maintenance (SB-UPSTREAM-002/003), next-settlement-day processing of client fund release requests (SB-UPSTREAM-005), and post-cut-off balance retention in USCNBA (SB-UPSTREAM-013).

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
