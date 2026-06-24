# TRAJ-T04: What obligations apply when an authorised person collects funds from clients?

Route chosen: **simple**  (gold: simple)  
Correction fired: False  (gold expects: False)  
Steps: 3  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | hybrid_search | `{"query": "authorised person collecting funds from clients",` | {'results': [{'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized P |
| 2 | hybrid_search | `{"query": "authorised person client fund collection prohibit` | {'results': [{'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized P |
| 3 | temporal_filter | `{"as_of": "2026-06-24"}` | {'as_of': '2026-06-24', 'valid_count': 54, 'valid_obligation_ids': '[54 ids]'} |
| 4 | rerank | `{"query": "authorised person collecting funds from clients o` | {'reranked': [{'obligation_id': 'SB-RUNACCT-010', 'title': '', 'score': 0.95}, { |
| 5 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-010"}` | {'obligation_id': 'SB-RUNACCT-010', 'title': 'Prohibit Authorized Person from Ac |
| 6 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-011"}` | {'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized Person Proprie |
| 7 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-002"}` | {'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated USCNBA for Re |
| 8 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-005"}` | {'obligation_id': 'SB-UPSTREAM-005', 'title': 'Process Client Fund Release Reque |
| 9 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-001"}` | {'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client Clear Credit  |

Gold tools: `['hybrid_search', 'rerank']`  
Actual tools: `['hybrid_search', 'hybrid_search', 'temporal_filter', 'rerank', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent']`  
Key tool (hybrid_search) hit: True

## Obligations returned
['SB-RUNACCT-010', 'SB-RUNACCT-011', 'SB-UPSTREAM-002', 'SB-UPSTREAM-005', 'SB-UPSTREAM-001']

## Reasoning
When an authorised person (AP) interacts with client funds, five currently-valid obligations apply: (1) SB-RUNACCT-010 flatly prohibits an AP from accepting client funds or securities and places the enforcement duty on the Trading Member; (2) SB-RUNACCT-011 restricts any proprietary trading by an AP to its own funds/securities only — never client funds; (3) SB-UPSTREAM-002 requires that all client funds received by the broker must go exclusively into a designated USCNBA (no other account), which directly governs the channel through which funds must flow even if an AP is the collection point; (4) SB-UPSTREAM-001 requires the broker to upstream all client clear credit balances to Clearing Corporations on an EOD basis; and (5) SB-UPSTREAM-005 governs timely processing of client fund-release requests (by the next settlement day). All five obligations are sourced from SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110, clause 47.7 and 93.x, and are valid as of 2026-06-24.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
