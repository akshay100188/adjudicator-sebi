# TRAJ-T01: Is our running-account settlement policy compliant as of today, and has anything changed in the underlying rules?

Route chosen: **multi-hop**  (gold: multi-hop)  
Correction fired: False  (gold expects: False)  
Steps: 7  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | temporal_filter | `{"as_of": "2026-07-04"}` | {'as_of': '2026-07-04', 'valid_count': 77, 'valid_obligation_ids': '[77 ids]'} |
| 2 | hybrid_search | `{"query": "running account settlement of client funds", "top` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 3 | hybrid_search | `{"query": "upstreaming of client funds broker settlement", "` | {'results': [{'obligation_id': 'SB-RUNACCT-015', 'title': 'Stock Exchange Online |
| 4 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-001"}` | {'obligation_id': 'SB-RUNACCT-001', 'title': 'Settle Running Account on Exchange |
| 5 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-001"}` | {'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client Clear Credit  |
| 6 | hybrid_search | `{"query": "running account settlement frequency 30 days 90 d` | {'results': [{'obligation_id': 'SB-RUNACCT-006', 'title': "Settle Running Accoun |
| 7 | graph_lookup | `{"circular_ref": "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110"}` | {'edges': [{'from_ref': 'SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110', 'to_ref': 'C |
| 8 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-006"}` | {'obligation_id': 'SB-RUNACCT-006', 'title': "Settle Running Account Only via Ac |
| 9 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-009"}` | {'obligation_id': 'SB-RUNACCT-009', 'title': 'Discontinue Retention of Funds for |
| 10 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-016"}` | {'obligation_id': 'SB-RUNACCT-016', 'title': 'Do Not Retain Excess Client Funds  |
| 11 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-003"}` | {'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Received Post-Set |
| 12 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-007"}` | {'obligation_id': 'SB-RUNACCT-007', 'title': 'Return Credit Balance to Inactive  |
| 13 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-012"}` | {'obligation_id': 'SB-RUNACCT-012', 'title': 'Send SMS and Email Settlement Inti |
| 14 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-013"}` | {'obligation_id': 'SB-RUNACCT-013', 'title': 'Send Retention Statement with Runn |
| 15 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-014"}` | {'obligation_id': 'SB-RUNACCT-014', 'title': 'Allow Client 30 Working Days to Ra |
| 16 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-015"}` | {'obligation_id': 'SB-RUNACCT-015', 'title': 'Stock Exchange Online Monitoring S |
| 17 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-002"}` | {'obligation_id': 'SB-RUNACCT-002', 'title': 'Adhere to Annual Settlement Calend |
| 18 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-004"}` | {'obligation_id': 'SB-RUNACCT-004', 'title': 'Retain Only Permissible Funds for  |
| 19 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-005"}` | {'obligation_id': 'SB-RUNACCT-005', 'title': 'Retain Only Permissible Funds for  |
| 20 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-008"}` | {'obligation_id': 'SB-RUNACCT-008', 'title': 'Use Date of Realisation as Settlem |
| 21 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-010"}` | {'obligation_id': 'SB-RUNACCT-010', 'title': 'Prohibit Authorized Person from Ac |
| 22 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-011"}` | {'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized Person Proprie |
| 23 | expand_to_parent | `{"obligation_id": "SB-EWMDS-015"}` | {'obligation_id': 'SB-EWMDS-015', 'title': 'Comply with Shortened Running Accoun |
| 24 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-002"}` | {'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated USCNBA for Re |
| 25 | rerank | `{"query": "running account settlement of client funds obliga` | {'reranked': [{'obligation_id': 'SB-RUNACCT-001', 'title': '', 'score': 0.95}, { |
| 26 | rerank | `{"query": "running account settlement client funds upstreami` | {'reranked': [{'obligation_id': 'SB-RUNACCT-014', 'title': '', 'score': 0.9}, {' |

Gold tools: `['temporal_filter', 'hybrid_search', 'graph_lookup', 'temporal_filter', 'rerank']`  
Actual tools: `['temporal_filter', 'hybrid_search', 'hybrid_search', 'expand_to_parent', 'expand_to_parent', 'hybrid_search', 'graph_lookup', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'rerank', 'rerank']`  
Key tool (graph_lookup) hit: True

## Obligations returned
['SB-RUNACCT-001', 'SB-RUNACCT-002', 'SB-RUNACCT-003', 'SB-RUNACCT-004', 'SB-RUNACCT-005', 'SB-RUNACCT-006', 'SB-RUNACCT-007', 'SB-RUNACCT-008', 'SB-RUNACCT-009', 'SB-RUNACCT-010', 'SB-RUNACCT-011', 'SB-RUNACCT-012', 'SB-RUNACCT-013', 'SB-RUNACCT-014', 'SB-RUNACCT-015', 'SB-RUNACCT-016', 'SB-UPSTREAM-001', 'SB-UPSTREAM-002', 'SB-UPSTREAM-003', 'SB-UPSTREAM-005', 'SB-UPSTREAM-013', 'SB-EWMDS-015']

## Reasoning
All 22 obligations are currently valid as of 2026-07-04 (confirmed by temporal_filter returning all SB-RUNACCT-* and SB-UPSTREAM-* IDs). Every obligation traces to the single master circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110, which is itself a consolidating circular — graph_lookup confirmed it consolidated 9 prior circulars (2018–2023) and superseded the immediately preceding CIR/2024/53, meaning the 2024/110 master circular IS the current authoritative source for running-account settlement rules and no further amendments are outstanding. The obligations cover: settlement frequency/calendar (SB-RUNACCT-001/002), post-settlement ring-fencing in USCNBA (SB-RUNACCT-003/SB-UPSTREAM-002), permissible fund retention caps for clients with open positions (SB-RUNACCT-004/005), ban on journal-entry settlement (SB-RUNACCT-006), 3-working-day return for inactive clients (SB-RUNACCT-007), physical instrument settlement dating (SB-RUNACCT-008), ban on admin-difficulty retention (SB-RUNACCT-009), authorized-person fund prohibitions (SB-RUNACCT-010/011), SMS/email intimation (SB-RUNACCT-012), 5-working-day retention statement (SB-RUNACCT-013), 30-working-day client dispute window (SB-RUNACCT-014), exchange monitoring system (SB-RUNACCT-015), no excess retention post-settlement (SB-RUNACCT-016), EOD upstreaming of clear credit balances to CCs (SB-UPSTREAM-001), USCNBA maintenance (SB-UPSTREAM-002/003/013), next-settlement-day fund release (SB-UPSTREAM-005), and shortened timelines under early-warning triggers (SB-EWMDS-015).

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
