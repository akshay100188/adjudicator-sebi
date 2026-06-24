# Review — Chapter 46: Validation of Instructions for Pay -In of Securities from Client demat account

Source (current): `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (2024-08-09)  
Consolidates: `SEBI/HO/MIRSD/DoP/P/CIR/2022/119` (September 19, 2022)

> Not legal advice. Approve/correct each obligation, then set `_approved: true`.

## Candidate obligations (7)

### SB-PAYINVAL-001 — Depository Validation of Pay-In Transfer Instructions Against CC Obligations
- **Clauses:** 46.1, 46.3, 46.3.1, 46.3.2, 46.3.3
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** Depositories must validate every transfer instruction received for Pay-In of securities from a client demat account to the Trading Member (TM) Pool account — whether initiated by the client directly or by a POA/DDPI holder — against the client-wise net delivery obligations received from Clearing Corporations (CCs), using parameters such as UCC, TM ID, CM ID, Exchange ID, ISIN, quantity, and settlement details, prior to executing the actual transfer.
- **Expected controls:** Automated matching engine that compares debit instructions against CC-provided client-wise net delivery obligation data on T day; Receipt and ingestion of CC obligation data (UCC, TM ID, CM ID, Exchange ID, ISIN, quantity, settlement details) into validation system on T day; Audit trail recording each Pay-In instruction received and the corresponding validation result

### SB-PAYINVAL-002 — CC to Provide Client-Wise Net Delivery Obligations to Depositories on T Day
- **Clauses:** 46.3.2
- **Category:** securities_settlement_validation · **Intermediary:** clearing_corporation
- **Obligation:** Clearing Corporations (CCs) must provide client-wise net delivery obligations to the depositories on T day to enable validation of Pay-In transfer instructions.
- **Expected controls:** Automated system to generate and transmit client-wise net delivery obligation data to depositories on T day; Reconciliation process to confirm successful delivery of obligation data to depositories; Timestamped logs of obligation data transmission to depositories

### SB-PAYINVAL-003 — Execution of Matched Pay-In Instructions
- **Clauses:** 46.3.4
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** Where all details of a Pay-In transfer instruction (UCC, TM ID, CM ID, ISIN, quantity, settlement details, etc.) match the CC obligation data, the depository must carry out the instruction by debiting securities from the client's demat account and crediting them to the linked TM Pool account on or before the settlement day.
- **Expected controls:** Automated processing workflow to execute matched Pay-In instructions by settlement day; System controls ensuring debit from client demat account and credit to linked TM Pool account are completed on or before settlement day; Confirmation notification generated upon successful execution of matched instructions

### SB-PAYINVAL-004 — Rejection of Pay-In Instructions with Mismatched Identifier Details
- **Clauses:** 46.3.5
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** Where there are discrepancies in key identifier details — such as UCC, TM ID, CM ID, or ISIN — between a Pay-In transfer instruction and the CC obligation data, the depository must reject such transfer instructions.
- **Expected controls:** Automated rejection workflow triggered upon mismatch of UCC, TM ID, CM ID, or ISIN between instruction and obligation data; Rejection notice generated and communicated to the relevant party upon rejection; Audit log of all rejected instructions with reasons for rejection

### SB-PAYINVAL-005 — Partial Processing of Pay-In Instructions Where Instruction Quantity Exceeds Obligation
- **Clauses:** 46.3.6, 46.3.6.1, 46.3.6.2
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** Where the quantity in a Pay-In transfer instruction differs from the CC obligation quantity: (a) if the instruction quantity is less than the obligation quantity, the depository must carry out the instruction in full; (b) if the instruction quantity is more than the obligation quantity, the depository must partially process the instruction up to the matching obligation quantity only.
- **Expected controls:** System logic to process Pay-In instructions in full when instruction quantity is less than or equal to obligation quantity; System logic to cap and partially process Pay-In instructions at the obligation quantity when instruction quantity exceeds obligation; Notification to relevant party when an instruction is partially processed, specifying the processed and unprocessed quantities; Audit trail of quantity comparison outcomes and resulting processing actions

### SB-PAYINVAL-006 — Early Pay-In Block Mechanism to Continue
- **Clauses:** 46.2
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** For Early Pay-In transactions, the existing block mechanism facility must continue to be available and operational.
- **Expected controls:** Maintenance and availability of the block mechanism for Early Pay-In transactions; Periodic testing to confirm the block mechanism remains operational

### SB-PAYINVAL-007 — Exemption of Custodian-Cleared Clients from Pay-In Validation Process
- **Clauses:** 46.3.7
- **Category:** securities_settlement_validation · **Intermediary:** depository
- **Obligation:** The Pay-In instruction validation process described in clause 46.3 does not apply to clients who have arrangements with SEBI-registered custodians for the clearing and settlement of their trades.
- **Expected controls:** System flag or configuration to identify and exclude clients with SEBI-registered custodian clearing arrangements from the Pay-In validation workflow; Periodic review to confirm that custodian-cleared client exemptions remain accurate and up to date

## Relation edges (1)

- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/DoP/P/CIR/2022/119`  (chapter 46 footnote: dated September 19, 2022)
