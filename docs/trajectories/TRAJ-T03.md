# TRAJ-T03: What's the position on client money sitting in our account?

Route chosen: **multi-hop**  (gold: multi-hop)  
Correction fired: False  (gold expects: True)  
Steps: 4  ·  Grounding dropped: none

## Steps
| # | tool | args | observation |
|---|---|---|---|
| 1 | hybrid_search | `{"query": "running account settlement of client funds stock ` | {'results': [{'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Rece |
| 2 | hybrid_search | `{"query": "client money retention upstreaming broker account` | {'results': [{'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated  |
| 3 | temporal_filter | `{"as_of": "2026-07-04"}` | {'as_of': '2026-07-04', 'valid_count': 77, 'valid_obligation_ids': '[77 ids]'} |
| 4 | rerank | `{"query": "client money retention running account settlement` | {'reranked': [{'obligation_id': 'SB-RUNACCT-016', 'title': '', 'score': 0.92}, { |
| 5 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-001"}` | {'obligation_id': 'SB-UPSTREAM-001', 'title': 'Upstream All Client Clear Credit  |
| 6 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-016"}` | {'obligation_id': 'SB-RUNACCT-016', 'title': 'Do Not Retain Excess Client Funds  |
| 7 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-003"}` | {'obligation_id': 'SB-RUNACCT-003', 'title': 'Ring-Fence Funds Received Post-Set |
| 8 | expand_to_parent | `{"obligation_id": "SB-UPSTREAM-002"}` | {'obligation_id': 'SB-UPSTREAM-002', 'title': 'Maintain Designated USCNBA for Re |
| 9 | graph_lookup | `{"circular_ref": "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110"}` | {'edges': [{'from_ref': 'SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110', 'to_ref': 'C |
| 10 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-015"}` | {'obligation_id': 'SB-RUNACCT-015', 'title': 'Stock Exchange Online Monitoring S |
| 11 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-009"}` | {'obligation_id': 'SB-RUNACCT-009', 'title': 'Discontinue Retention of Funds for |
| 12 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-006"}` | {'obligation_id': 'SB-RUNACCT-006', 'title': "Settle Running Account Only via Ac |
| 13 | expand_to_parent | `{"obligation_id": "SB-RUNACCT-013"}` | {'obligation_id': 'SB-RUNACCT-013', 'title': 'Send Retention Statement with Runn |

Gold tools: `['hybrid_search', 'rerank', 'hybrid_search']`  
Actual tools: `['hybrid_search', 'hybrid_search', 'temporal_filter', 'rerank', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'graph_lookup', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent', 'expand_to_parent']`  
Key tool (rerank) hit: True

## Obligations returned
['SB-RUNACCT-016', 'SB-RUNACCT-015', 'SB-UPSTREAM-001', 'SB-UPSTREAM-002', 'SB-RUNACCT-003', 'SB-RUNACCT-006', 'SB-RUNACCT-009', 'SB-RUNACCT-013']

## Reasoning
Client money sitting in a broker's account is governed by two interlocking frameworks — (1) Running Account Settlement (clauses 47.x): the broker must not retain excess client funds after settlement (SB-RUNACCT-016), settlement is valid only via actual payment to the client's bank account and not by journal entry (SB-RUNACCT-006), administrative/operational difficulties are no longer a valid reason to retain active-client funds (SB-RUNACCT-009), a retention statement must be sent within 5 working days (SB-RUNACCT-013), and Stock Exchanges monitor compliance online (SB-RUNACCT-015); and (2) Upstreaming Framework (clauses 93.x): all clear client credit balances must be upstreamed to Clearing Corporations on an EOD basis in the form of cash/FDR lien/MFOS pledge (SB-UPSTREAM-001), all client funds must be received only in the designated USCNBA (SB-UPSTREAM-002), and post-settlement receipts must be ring-fenced in the USCNBA and not used for other clients (SB-RUNACCT-003). All obligations flow from the current master consolidated circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110, which consolidates all prior circulars from 2018 onwards and supersedes 2024/53; confirmed valid as of 2026-07-04.

> This output does not constitute legal advice or a compliance determination. All findings require review by a qualified compliance professional. Always verify against the cited source circular.
