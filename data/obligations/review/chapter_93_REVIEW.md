# Review — Chapter 93: Upstreaming of clients' funds by Stock Brokers (SBs) / Clea ring Members

Source (current): `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (2024-08-09)  
Consolidates: `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/187` (December 12, 2023)

> Not legal advice. Approve/correct each obligation, then set `_approved: true`.

## Candidate obligations (14)

### SB-UPSTREAM-001 — Upstream All Client Clear Credit Balances to CCs on EOD Basis
- **Clauses:** 93.1
- **Category:** client_funds_upstreaming · **Intermediary:** trading_member
- **Obligation:** Stock Brokers (SBs) and Clearing Members (CMs) must upstream all clients' clear credit balances to Clearing Corporations (CCs) on an End of Day (EOD) basis. Such upstreaming shall be done only in the form of: (a) cash, (b) lien on Fixed Deposit Receipts (FDRs) created out of clients' funds, or (c) pledge of units of Mutual Fund Overnight Schemes (MFOS) created out of clients' funds.
- **Expected controls:** Daily EOD process to calculate and upstream all client clear credit balances to CCs; Controls restricting upstreaming instruments to only cash, FDR liens, or MFOS pledge; Reconciliation report confirming full upstreaming completion each EOD; Exception reporting for any balances not upstreamed by EOD

### SB-UPSTREAM-002 — Maintain Designated USCNBA for Receipt of Client Funds
- **Clauses:** 93.2
- **Category:** client_funds_accounts · **Intermediary:** trading_member
- **Obligation:** Stock Brokers/CMs must maintain a designated Up Streaming Client Nodal Bank Account (USCNBA) specifically for receiving funds from clients. This account must be named 'Name of the SB/CM – USCNB account'. No client funds shall be received in any account other than the USCNBA.
- **Expected controls:** Dedicated USCNBA bank account opened and named per prescribed nomenclature; System controls ensuring all incoming client fund transfers are routed only to USCNBA; Periodic audit to confirm no client funds are received in non-designated accounts

### SB-UPSTREAM-003 — Maintain Designated DSCNBA for Payment of Funds to Clients
- **Clauses:** 93.2
- **Category:** client_funds_accounts · **Intermediary:** trading_member
- **Obligation:** Stock Brokers/CMs must maintain a designated Down Streaming Client Nodal Bank Account (DSCNBA) and ensure that all payments to clients are made only from this account. This account must be named 'Name of the SB/CM – DSCNB account'.
- **Expected controls:** Dedicated DSCNBA bank account opened and named per prescribed nomenclature; System controls ensuring all outgoing client fund payments are routed only from DSCNBA; Periodic audit to confirm no client payments are made from non-designated accounts

### SB-UPSTREAM-004 — CMs to Use Designated Proprietary Account for Funds Received from/Paid to SBs
- **Clauses:** 93.3
- **Category:** client_funds_accounts · **Intermediary:** clearing_member
- **Obligation:** Clearing Members who clear trades for other Stock Brokers must use only designated bank accounts with the nomenclature 'Name of the CM – TM prop account' to receive and pay proprietary funds from/to those stock brokers.
- **Expected controls:** Dedicated TM prop account maintained with correct nomenclature; System controls restricting proprietary fund flows with SBs to the designated TM prop account only; Periodic audit confirming no proprietary SB/CM fund flows occur through other accounts

### SB-UPSTREAM-005 — Process Client Fund Release Requests by Next Settlement Day
- **Clauses:** 93.4
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** SBs/CMs must allow clients to request release of funds at any time during the day. Processing of such requests must follow the SB/CM's risk management practices. All client payment requests received on a given day must be processed on or before the next settlement day. Where a payment request is not processed on the same day, the SB/CM must ensure that the client's funds are placed with a CC in accordance with the upstreaming framework.
- **Expected controls:** Documented risk management policy governing processing of client fund release requests; System tracking of all client payment requests with timestamps and processing status; Automated escalation if any payment request is not processed by next settlement day; Controls ensuring unprocessed same-day requests result in placement of client funds with CC

### SB-UPSTREAM-006 — Ensure FDRs Created from Client Funds Meet Prescribed Conditions
- **Clauses:** 93.5
- **Category:** client_funds_fdrs · **Intermediary:** trading_member
- **Obligation:** FDRs created by SBs/CMs out of clients' funds must satisfy all of the following conditions: (a) created only with banks meeting CC exposure norms as specified by CCs/SEBI; (b) created only from the USCNBA; (c) lien-marked to a CC at all times, with the CC having explicit precedence over all other stakeholders including the FDR-issuing bank; (d) tenor not exceeding one year and one day, and must be pre-terminable on demand; (e) principal amount fully protected throughout tenure including after all pre-termination costs; (f) SBs/CMs must not avail any funded or non-funded banking facilities based on these FDRs.
- **Expected controls:** Pre-approved list of banks meeting CC exposure norms maintained and reviewed regularly; Process controls ensuring FDRs are created only from USCNBA and lien-marked to CC at creation; FDR register tracking tenor, pre-terminability, principal protection, and lien status for each FDR; Policy and system controls prohibiting use of client-fund FDRs as collateral for any banking facility

### SB-UPSTREAM-007 — Grandfather Existing Long-Tenor FDRs and Ensure Renewal Compliance
- **Clauses:** 93.6
- **Category:** client_funds_fdrs · **Intermediary:** trading_member
- **Obligation:** Existing FDRs created out of clients' funds with a tenor of more than one year that were created prior to June 30, 2023 are permitted to continue (grandfathered) until their maturity. Upon renewal, such FDRs must meet all conditions specified in clause 93.5.
- **Expected controls:** Register identifying all grandfathered FDRs with creation date, maturity date, and tenor; Automated alerts prior to maturity of grandfathered FDRs to trigger compliance review before renewal; Renewal checklist ensuring all conditions in clause 93.5 are satisfied before FDR renewal

### SB-UPSTREAM-008 — Invest Client Funds in Eligible MFOS Only (Government Securities/TREPS)
- **Clauses:** 93.8
- **Category:** client_funds_mfos · **Intermediary:** trading_member
- **Obligation:** SBs/CMs must ensure that client funds invested in Mutual Fund Overnight Schemes (MFOS) are placed only in schemes that deploy funds exclusively into risk-free government bond overnight repo markets and overnight Tri-party Repo Dealing and Settlement (TREPS). MFOS units must be held in dematerialized (demat) form and must be pledged with a CC at all times.
- **Expected controls:** Approved list of eligible MFOS schemes verified to invest only in government overnight repo/TREPS; Controls ensuring MFOS units are subscribed and held only in demat form; Automated process to pledge MFOS units with CC immediately upon subscription; Regular monitoring to confirm MFOS units remain pledged with CC at all times

### SB-UPSTREAM-009 — Maintain Dedicated Demat Account (Client Nodal MFOS Account) for MFOS Transactions
- **Clauses:** 93.9
- **Category:** client_funds_mfos · **Intermediary:** trading_member
- **Obligation:** SBs/CMs must maintain a dedicated demat account referred to as the 'Client Nodal MFOS Account' exclusively for subscription and redemption of MFOS units. Depositories are required to allow subscription/redemption transactions only in this designated account.
- **Expected controls:** Dedicated 'Client Nodal MFOS Account' demat account established and registered with depositories; Confirmation from depository that subscription/redemption transactions are restricted to this account; Periodic reconciliation of MFOS unit transactions against this account

### SB-UPSTREAM-010 — Pledge MFOS Units to CC via Pledge Re-Pledge Mechanism with Client Identification
- **Clauses:** 93.10
- **Category:** client_funds_mfos · **Intermediary:** trading_member
- **Obligation:** From the 'Client Nodal MFOS Account', SBs/CMs must provide MFOS units as collateral to the CC and must identify the end clients at the time of providing collateral. To implement this, a pledge must be created from the Client Nodal MFOS account to the SB/CM's margin pledge account, and the SB/CM must further re-pledge those units to the CC using the existing pledge re-pledge mechanism.
- **Expected controls:** Process for creating pledge from Client Nodal MFOS Account to SB/CM margin pledge account; Process for re-pledging MFOS units from SB/CM margin pledge account to CC; System to record and report end-client identification for each pledged MFOS unit; Reconciliation of pledged units at CC level against client-level records

### SB-UPSTREAM-011 — Prohibit Upstreaming of Client-Provided Bank Instruments (FDRs/BGs) to CCs
- **Clauses:** 93.13
- **Category:** client_collateral_eligibility · **Intermediary:** trading_member
- **Obligation:** Bank instruments provided by clients as collateral (i.e., client FDRs and Bank Guarantees) must not be upstreamed to CCs and are ineligible to be accepted as collateral in any segment of the securities market.
- **Expected controls:** System controls blocking submission of client-provided FDRs or BGs as collateral to CCs; Policy documentation clearly prohibiting upstreaming of client bank instruments; Regular audit to confirm no client FDRs or BGs have been upstreamed or submitted as collateral

### SB-UPSTREAM-012 — Comply with Conditions for Acceptance of Bank Guarantees from Non-Individual Clients in Commodity Derivatives
- **Clauses:** 93.14
- **Category:** client_collateral_eligibility · **Intermediary:** trading_member
- **Obligation:** By exception, Bank Guarantees (BGs) provided only by non-individual clients may be accepted as collateral in the commodity derivatives market, subject to all of the following conditions: (a) the client provides a declaration and undertaking that they shall have no recourse to SEBI or exchanges in case of wrongful invocation of the BG by the SB/CM; (b) the BG must contain a condition that upon invocation, proceeds are credited only to the USCNBA and thereafter upstreamed to the CC; and (c) any additional conditions specified in Annexure 44 and any stricter conditions imposed by CCs based on their risk assessment must be met.
- **Expected controls:** Client onboarding checklist to obtain signed declaration from non-individual clients before accepting BGs; Template BG vetted to include mandatory condition directing invocation proceeds to USCNBA; Process to upstream BG invocation proceeds from USCNBA to CC immediately upon receipt; Compliance review against Annexure 44 conditions and any CC-specific stricter requirements

### SB-UPSTREAM-013 — Retain Unupstreamed Client Balances in USCNBA Until Next-Day Upstreaming
- **Clauses:** 93.15
- **Category:** client_funds_upstreaming · **Intermediary:** trading_member
- **Obligation:** The cut-off times for upstreaming of clients' clear credit balances shall be as determined by CCs in consultation with ISF. Any client clear credit balance that could not be upstreamed to CCs due to client funds being received after the applicable cut-off time must remain in the USCNBA until it is upstreamed to the CC on the next day.
- **Expected controls:** System awareness of CC-determined cut-off times for upstreaming, updated as CCs revise them; Controls ensuring any post-cut-off client funds received remain in USCNBA and are not transferred elsewhere; Next-day upstreaming process triggered automatically for all balances held in USCNBA overnight; Daily reconciliation confirming no client funds remain in USCNBA beyond the next upstreaming cycle

### SB-UPSTREAM-014 — Scope Exclusion: Framework Not Applicable to Bank-CMs and Proprietary Funds
- **Clauses:** 93.16
- **Category:** client_funds_upstreaming · **Intermediary:** trading_member
- **Obligation:** The upstreaming framework does not apply to: (a) bank-CMs (including Custodians that are banks); (b) proprietary funds of SBs/CMs in any segment; and (c) SB proprietary funds deposited with a CM in the capacity of a client. SBs/CMs must ensure that controls and processes implementing the upstreaming framework are scoped correctly to exclude these categories.
- **Expected controls:** Documented scope definition clearly excluding bank-CMs, proprietary funds, and SB funds held as client by CM; System segregation ensuring proprietary fund accounts are not subjected to client upstreaming workflows; Periodic review confirming excluded categories remain correctly carved out from the framework

## Relation edges (1)

- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/187`  (chapter 93 footnote: dated December 12, 2023)
