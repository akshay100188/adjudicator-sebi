# TRAJ-T02: How often must running accounts be settled?

Route chosen: **simple**  (gold: simple)  
Correction fired: False  (gold expects: False)  
Steps: 3  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | temporal_filter | `{"as_of": "2026-07-04"}` | {'as_of': '2026-07-04', 'valid_count': 77, 'valid_obligation_ids': '[77 ids]'} |
| 2 | hybrid_search | `{"query": "running account settlement of client funds freque` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 3 | rerank | `{"query": "how often must running accounts be settled freque` | {'reranked': [{'obligation_id': 'SB-RUNACCT-001', 'title': '', 'score': 0.9}, {' |
| 4 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-001"}` | {'obligation_id': 'SB-RUNACCT-001', 'title': 'Settle Running Account on Exchange |
| 5 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-002"}` | {'obligation_id': 'SB-RUNACCT-002', 'title': 'Adhere to Annual Settlement Calend |
| 6 | expand_to_parent | `{"obligation_id": "SB-EWMDS-015"}` | {'obligation_id': 'SB-EWMDS-015', 'title': 'Comply with Shortened Running Accoun |
| 7 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-007"}` | {'obligation_id': 'SB-RUNACCT-007', 'title': 'Return Credit Balance to Inactive  |

Gold tools: `['hybrid_search', 'rerank']`  
Actual tools: `['temporal_filter', 'hybrid_search', 'rerank', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent']`  
Key tool (hybrid_search) hit: True

## Obligations returned
['SB-RUNACCT-001', 'SB-RUNACCT-002', 'SB-RUNACCT-007', 'SB-EWMDS-015']

## Reasoning
SB-RUNACCT-001 establishes the core rule: Trading Members must settle clients' running accounts on either a quarterly or monthly basis (per each client's choice), on dates stipulated by the Stock Exchanges. SB-RUNACCT-002 requires TMs to follow an annual settlement calendar jointly issued by the Exchanges at the start of each financial year. SB-RUNACCT-007 adds a special case: for inactive clients (no transaction in the past 30 calendar days), any credit balance must be returned within 3 working days regardless of the regular settlement cycle. SB-EWMDS-015 further mandates compliance with any shortened settlement timelines prescribed by Stock Exchanges under early-warning monitoring. All four obligations are currently valid as of 2026-07-04, sourced from SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
