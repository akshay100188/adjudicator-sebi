# TRAJ-T02: How often must running accounts be settled?

Route chosen: **simple**  (gold: simple)  
Correction fired: False  (gold expects: False)  
Steps: 2  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | hybrid_search | `{"query": "running account settlement of client funds freque` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 2 | temporal_filter | `{"as_of": "2026-06-24"}` | {'as_of': '2026-06-24', 'valid_count': 54, 'valid_obligation_ids': '[54 ids]'} |
| 3 | rerank | `{"query": "how often must running accounts be settled freque` | {'reranked': [{'obligation_id': 'SB-RUNACCT-001', 'title': '', 'score': 0.95}, { |
| 4 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-001"}` | {'obligation_id': 'SB-RUNACCT-001', 'title': 'Settle Running Account on Exchange |

Gold tools: `['hybrid_search', 'rerank']`  
Actual tools: `['hybrid_search', 'temporal_filter', 'rerank', 'expand_to_parent']`  
Key tool (hybrid_search) hit: True

## Obligations returned
['SB-RUNACCT-001']

## Reasoning
SB-RUNACCT-001 directly mandates the settlement frequency: Trading Members must settle clients' running accounts on either a quarterly or monthly basis (per the client's choice), on the specific dates stipulated by the Stock Exchanges — after considering the end-of-day (EOD) fund obligations across all exchanges. This obligation (sourced from SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110, clause 47.1.1) is confirmed currently valid as of 2026-06-24.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
