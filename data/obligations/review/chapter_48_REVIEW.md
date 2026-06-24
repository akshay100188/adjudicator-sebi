# Review — Chapter 48: Risk disclosure with respect to trading by individual traders in Equity Futures

Source (current): `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (2024-08-09)  
Consolidates: `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/73` (May 19, 2023)

> Not legal advice. Approve/correct each obligation, then set `_approved: true`.

## Candidate obligations (4)

### SB-RISKDISC-001 — Display F&O Risk Disclosures on Website and to All Clients
- **Clauses:** 48.2
- **Category:** risk_disclosure · **Intermediary:** trading_member
- **Obligation:** All stock brokers shall display the 'Risk disclosures' (as specified in Annexure-23) on their websites and to all their clients in the manner prescribed in clauses 48.2.1 and 48.2.2.
- **Expected controls:** Annexure-23 risk disclosure content published and kept current on the broker's public website; Process to disseminate risk disclosures to all clients through the trading platform; Periodic review to confirm disclosures remain displayed and up to date

### SB-RISKDISC-002 — Prompt Client Acknowledgement of F&O Risk Disclosures at Login
- **Clauses:** 48.2.1
- **Category:** risk_disclosure · **Intermediary:** trading_member
- **Obligation:** Upon login into their trading accounts, clients must be prompted to read the 'Risk disclosures' (e.g., via a pop-up window at login) and must acknowledge the disclosures before being allowed to proceed further into the trading platform.
- **Expected controls:** Login workflow configured to display Annexure-23 risk disclosure as a mandatory pop-up or interstitial screen; System enforces blocking of further platform access until client acknowledgement is recorded; Audit trail capturing client acknowledgement timestamp and identity for each login event

### SB-RISKDISC-003 — Risk Disclosures Must Cover at Least 50% of the Screen Area
- **Clauses:** 48.2.2
- **Category:** risk_disclosure · **Intermediary:** trading_member
- **Obligation:** When displaying the 'Risk disclosures' to clients, stock brokers must ensure the disclosure is displayed prominently, covering at least 50 percent of the screen area.
- **Expected controls:** UI/UX specification documented confirming the risk disclosure display element occupies a minimum of 50% of the screen area; Periodic UI testing (across device types and screen sizes) to verify the 50% screen coverage requirement is met

### SB-RISKDISC-004 — QSBs to Maintain Client F&O P&L Data Continuously and Retain for 5 Years
- **Clauses:** 48.3
- **Category:** recordkeeping · **Intermediary:** trading_member
- **Obligation:** All Qualified Stock Brokers (QSBs) must maintain Profit and Loss (P&L) data of their clients on a continuous basis in the format specified in Annexure-24, and must retain such P&L data for a minimum period of 5 years.
- **Expected controls:** Automated system configured to capture and record client-level F&O P&L data continuously in the Annexure-24 prescribed format; Data retention policy and storage infrastructure ensuring client P&L records are preserved for at least 5 years; Periodic data integrity checks to confirm completeness and accuracy of retained P&L records; Access controls and backup procedures protecting archived P&L data from loss or unauthorised modification

## Relation edges (1)

- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/73`  (chapter 48 footnote: dated May 19, 2023)
