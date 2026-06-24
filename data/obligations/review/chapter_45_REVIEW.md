# Review — Chapter 45: Handling of Client's Securities by Trading Members/ Clearing Members

Source (current): `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (2024-08-09)  
Consolidates: `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2022/153` (June 20, 2019)

> Not legal advice. Approve/correct each obligation, then set `_approved: true`.

## Candidate obligations (11)

### SB-CLTSEC-001 — Transfer of Securities to Client Demat Account Within One Working Day of Pay-out
- **Clauses:** 45.1.1
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** All securities received in pay-out must be transferred from the TM/CM's pool account directly to the demat account of the respective client within one working day of the pay-out.
- **Expected controls:** Automated system to initiate transfer of pay-out securities from pool account to client demat account within one working day; Daily reconciliation report confirming timely transfer of all pay-out securities to respective client demat accounts; Exception alert mechanism for any transfer not completed within the one working day deadline

### SB-CLTSEC-002 — Transfer of Unpaid Securities to Client Demat Account with Auto-Pledge Creation
- **Clauses:** 45.1.2
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** Unpaid securities (securities not paid for in full by the client) must be transferred to the respective client's demat account and immediately subjected to an auto-pledge (without requiring a specific instruction from the client), with the reason coded as 'unpaid', in favour of a separate account titled 'client unpaid securities pledgee account' maintained by the TM/CM.
- **Expected controls:** Maintenance of a dedicated 'client unpaid securities pledgee account' opened by the TM/CM; Automated system to identify unpaid securities and create auto-pledge with reason 'unpaid' without manual client instruction; Reconciliation process to verify all unpaid securities are pledged to the correct pledgee account after transfer to client demat

### SB-CLTSEC-003 — Communication to Client After Pledge Creation on Unpaid Securities
- **Clauses:** 45.1.3
- **Category:** client_communication · **Intermediary:** trading_member
- **Obligation:** After creation of the pledge on unpaid securities, the TM/CM must send a communication (via email and/or SMS) to the client informing them of their funds obligation and notifying them of the TM/CM's right to sell the pledged securities if the client fails to fulfil that obligation.
- **Expected controls:** Automated email/SMS notification triggered upon pledge creation containing details of funds obligation and TM/CM's right to sell; Delivery and read-receipt logging for all pledge-creation communications; Template-based communication process ensuring all required disclosures (obligation amount, sale right) are included

### SB-CLTSEC-004 — Release of Pledge When Client Fulfils Funds Obligation Within Five Trading Days
- **Clauses:** 45.1.4
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** If a client fulfils their funds obligation within five trading days after the pay-out, the TM/CM must release the pledge on the unpaid securities so that the securities become available to the client as a free balance.
- **Expected controls:** Daily monitoring of client payment status against outstanding funds obligations for unpaid securities; Automated or same-day pledge release process triggered upon confirmation of full funds receipt from the client; Audit trail recording date and time of client payment and corresponding pledge release

### SB-CLTSEC-005 — Disposal of Unpaid Securities and Pre-Sale Intimation When Client Does Not Fulfil Obligation
- **Clauses:** 45.1.5
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** If a client does not fulfil their funds obligation within five trading days after the pay-out, the TM/CM must dispose of the unpaid securities in the market within five trading days after the pay-out. Before disposing of the securities, the TM/CM must send an intimation (via email and/or SMS) to the client one trading day before the sale.
- **Expected controls:** Automated tracking of the five-trading-day deadline per client for unpaid securities; Automated email/SMS pre-sale intimation to the client one trading day before scheduled disposal; Documented disposal execution process with timestamps confirming sale within the prescribed five-trading-day window; Delivery receipt records for all pre-sale intimation communications

### SB-CLTSEC-006 — Sale of Unpaid Securities Using Client's UCC and Adjustment of Profit/Loss to Client Account
- **Clauses:** 45.1.6
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** When unpaid securities are sold in the market, the sale transaction must be executed using the Unique Client Code (UCC) of the respective client. Any profit or loss arising from the sale must be transferred to or adjusted from the respective client's account.
- **Expected controls:** System enforcement that unpaid securities sale orders are placed under the client's UCC; Automated calculation and posting of profit or loss from each sale transaction to the corresponding client account; Reconciliation report confirming UCC usage and P&L adjustments for all unpaid securities disposals

### SB-CLTSEC-007 — Pledge Invocation Restricted to Client's Delivery Obligation with Early Pay-in Block
- **Clauses:** 45.1.7
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** The TM/CM may invoke the pledge on unpaid securities only against the delivery obligation of the respective client. Upon invocation, the securities must be blocked for early pay-in in the client's demat account, and a corresponding trail must be maintained in the TM/CM's client unpaid securities pledgee account.
- **Expected controls:** System controls restricting pledge invocation to the quantum of the client's verified delivery obligation; Process to block invoked securities for early pay-in in the client's demat account immediately upon invocation; Maintenance of an auditable trail in the client unpaid securities pledgee account for each pledge invocation event

### SB-CLTSEC-008 — Depository Verification of Blocked Securities Against Client-Level Obligation
- **Clauses:** 45.1.8
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** Once unpaid securities are blocked for early pay-in in the client's demat account following pledge invocation, the depositories must verify the block details against the client-level delivery obligation.
- **Expected controls:** Coordination with depositories to ensure a verification mechanism is in place for block details vs. client-level obligation; Confirmatory reporting from depositories upon completion of verification of blocked securities

### SB-CLTSEC-009 — Auto-Release of Pledge If Not Invoked or Released Within Seven Trading Days
- **Clauses:** 45.1.9
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** If the pledge on unpaid securities is neither invoked nor released within seven trading days after the pay-out, the pledge must be automatically released and the securities must become available to the client as free balance without any encumbrance.
- **Expected controls:** Automated pledge management system that triggers auto-release of pledge on the seventh trading day after pay-out if no invocation or voluntary release has occurred; Post-release confirmation report verifying securities are reflected as free balance in the client's demat account; Exception log for any auto-release failures requiring manual intervention

### SB-CLTSEC-010 — Unpaid Securities Not to be Considered for Client's Margin Obligations
- **Clauses:** 45.1.10
- **Category:** margin_management · **Intermediary:** trading_member
- **Obligation:** Unpaid securities pledged in a client's account under the 'client unpaid securities pledgee account' arrangement must not be considered or applied towards meeting the margin obligations of that client.
- **Expected controls:** System configuration to exclude securities held in the client unpaid securities pledgee account from margin collateral calculations; Periodic reconciliation to confirm that no unpaid pledged securities have been erroneously included in client margin computations

### SB-CLTSEC-011 — Prohibition on Pledging or Transferring Unpaid Client Securities to Banks/NBFCs
- **Clauses:** 45.2.2
- **Category:** client_securities_handling · **Intermediary:** trading_member
- **Obligation:** Securities lying with the TM/CM in the client unpaid securities pledgee account must not be pledged or transferred to Banks or NBFCs by the TM/CM for the purpose of raising funds.
- **Expected controls:** System-level restriction preventing initiation of any pledge or transfer instruction from the client unpaid securities pledgee account to Banks/NBFCs; Periodic audit of the client unpaid securities pledgee account to confirm no such pledge or transfer has occurred; Alert mechanism triggered if any attempt is made to pledge or transfer securities from this account to a Bank or NBFC

## Relation edges (2)

- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2022/153`  (chapter 45 footnote: dated June 20, 2019)
- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --supersedes--> `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/53`  (successor master circular for stock brokers)
