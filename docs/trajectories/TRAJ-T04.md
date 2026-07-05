# TRAJ-T04: What obligations apply when an authorised person collects funds from clients?

Route chosen: **simple**  (gold: simple)  
Correction fired: False  (gold expects: False)  
Steps: 4  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | hybrid_search | `{"query": "authorised person collects funds from clients", "` | {'results': [{'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized P |
| 2 | hybrid_search | `{"query": "authorised person collection of money securities ` | {'results': [{'obligation_id': 'SB-CLTSEC-002', 'title': 'Transfer of Unpaid Sec |
| 3 | temporal_filter | `{"as_of": "2026-07-04"}` | {'as_of': '2026-07-04', 'valid_count': 77, 'valid_obligation_ids': '[77 ids]'} |
| 4 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-010"}` | {'obligation_id': 'SB-RUNACCT-010', 'title': 'Prohibit Authorized Person from Ac |
| 5 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-011"}` | {'obligation_id': 'SB-RUNACCT-011', 'title': 'Restrict Authorized Person Proprie |
| 6 | rerank | `{"query": "authorised person collecting funds or securities ` | {'reranked': [{'obligation_id': 'SB-RUNACCT-010', 'title': '', 'score': 0.95}, { |
| 7 | expand_to_parent | `{"obligation_id": "SB-EWMDS-010"}` | {'obligation_id': 'SB-EWMDS-010', 'title': 'Prohibit Pledging of Securities of C |
| 8 | expand_to_parent | `{"obligation_id": "SB-EWMDS-018"}` | {'obligation_id': 'SB-EWMDS-018', 'title': 'Cooperate with Forensic Audit When C |
| 9 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-002"}` | {'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated USCNBA for Re |
| 10 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-003"}` | {'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Received Post-Set |
| 11 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-013"}` | {'obligation_id': 'SB-UPSTREAM-013', 'title': 'Retain Unupstreamed Client Balanc |

Gold tools: `['hybrid_search', 'rerank']`  
Actual tools: `['hybrid_search', 'hybrid_search', 'temporal_filter', 'expand_to_parent', 'expand_to_parent', 'rerank', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent']`  
Key tool (hybrid_search) hit: True

## Obligations returned
['SB-RUNACCT-010', 'SB-RUNACCT-011', 'SB-UPSTREAM-002', 'SB-RUNACCT-003', 'SB-UPSTREAM-013']

## Reasoning
When an Authorised Person (AP) collects funds from clients, the primary obligation is SB-RUNACCT-010 (absolute prohibition on APs accepting client funds or securities) and SB-RUNACCT-011 (any AP proprietary trading must use only the AP's own funds/securities, not client money). On the Trading Member (TM) side, SB-UPSTREAM-002 requires that all client funds be received exclusively into a designated Up Streaming Client Nodal Bank Account (USCNBA) — no other account may be used — which directly controls the channel through which funds legitimately flow. SB-RUNACCT-003 ring-fences post-settlement receipts in the USCNBA so they cannot be co-mingled with other clients' running accounts, and SB-UPSTREAM-013 requires any client balances not yet upstreamed to CCs (due to cut-off timing) to remain in the USCNBA until next-day upstreaming. All five obligations originate from SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110 and are currently valid as of 2026-07-04.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
