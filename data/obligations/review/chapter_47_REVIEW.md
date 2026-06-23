# Review — Chapter 47: Settlement of Running Account of Client's Funds lying with Trading Member

Source (current): `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` (2024-08-09)  
Supersedes: `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/53`  
Consolidates: `SEBI/HO/MIRSD/DOP/P/CIR/2021/577` (June 16,2021), `SEBI/HO/MIRSD/DOP/P/CIR/2022/101` (July 27, 2022), `SEBI/HO/MIRSD/MIRSD-PoD1/P/CIR/2023/197` (December 28, 2023)

> Not legal advice. Approve/correct each obligation, then set `_approved: true` in the JSON.

## Candidate obligations (13)

### SB-RUNACCT-001 — Settle Running Account on Exchange-Stipulated Dates per Client Choice
- **Clauses:** 47.1.1
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** The Trading Member (TM), after considering the End of the Day (EOD) obligation of funds across all Exchanges, must settle clients' running accounts on either a quarterly or monthly basis (as chosen by each client), on the dates stipulated by the Stock Exchanges.
- **Expected controls:** Maintain a client-level record of each client's chosen settlement frequency (monthly/quarterly); Automated scheduling system aligned to Stock Exchange-stipulated settlement dates; EOD fund obligation aggregation process across all Exchanges before initiating settlement; Pre-settlement checklist confirming dates match Exchange-published calendar

### SB-RUNACCT-002 — Adhere to Annual Settlement Calendar Issued by Stock Exchanges
- **Clauses:** 47.1.2
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** Stock Exchanges shall jointly issue, at the beginning of each financial year, an annual calendar specifying all running account settlement dates for both quarterly and monthly cycles. The TM must adhere to this calendar when scheduling settlements.
- **Expected controls:** Annual retrieval and storage of the Exchange-issued settlement calendar at the start of each financial year; System configuration to flag and schedule settlement runs as per the published calendar

### SB-RUNACCT-003 — Ring-Fence Funds Received Post-Settlement in Up Streaming Client Nodal Bank Account
- **Clauses:** 47.1.3
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** After a client's running account has been settled, any funds subsequently received from that client must remain in the 'Up Streaming Client Nodal Bank Account' and must not be used for the settlement of running accounts of other clients.
- **Expected controls:** Segregated 'Up Streaming Client Nodal Bank Account' with system controls preventing cross-utilisation of post-settlement client funds; Automated reconciliation to verify that post-settlement receipts are not applied to other clients' obligations; Daily monitoring report flagging any commingling of post-settlement funds

### SB-RUNACCT-004 — Retain Only Permissible Funds for Clients with Outstanding Positions on Settlement Date – Pay-in Obligation
- **Clauses:** 47.2, 47.2.1
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** Where a client has any outstanding trade position on the scheduled running account settlement date, the TM may retain the entire pay-in obligation of funds outstanding at the end of the day for T day and T-1 day across all Exchanges.
- **Expected controls:** System capability to compute and capture EOD pay-in obligations for T and T-1 days per client across all Exchanges on the settlement date; Automated retention calculation that limits retention to the computed T and T-1 pay-in obligation amounts

### SB-RUNACCT-005 — Retain Only Permissible Funds for Clients with Outstanding Positions on Settlement Date – Margin Liability Cap
- **Clauses:** 47.2, 47.2.2
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** Where a client has any outstanding trade position on the scheduled running account settlement date, the TM may additionally retain margin liability as on that date across all segments and Exchanges, including additional margins up to a maximum of 125% of total margin liability. The margin liability computation shall exclude MTM and pay-in obligations, and the TM may therefore retain up to 225% of total margin liability in aggregate across all segments and Exchanges.
- **Expected controls:** System to compute total margin liability per client (excluding MTM and pay-in obligations) across all segments and Exchanges on settlement date; Automated cap enforcement ensuring additional margin retention does not exceed 125% of total margin liability (total retention ≤ 225%); Retention computation audit trail available for Exchange monitoring and internal review

### SB-RUNACCT-006 — Settle Running Account Only via Actual Payment to Client's Bank Account
- **Clauses:** 47.3
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** A client's running account shall be considered settled only when actual payment is made into the client's bank account. Settlement must not be effected by journal entries. Journal entries in a client's account are permitted solely for the levy or reversal of charges in that client's account.
- **Expected controls:** System control preventing running account settlement entries from being processed via journal entries; Workflow requiring an actual bank transfer record (transaction reference) before marking an account as settled; Periodic audit to confirm no settlement has been recorded through journal entries other than charge levy/reversal

### SB-RUNACCT-007 — Return Credit Balance to Inactive Clients Within Three Working Days
- **Clauses:** 47.4
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** For clients who have a credit balance and have not conducted any transaction in the 30 calendar days since their last transaction, the TM must return the credit balance to the client within the next three working days, irrespective of when the running account was previously settled.
- **Expected controls:** Automated daily identification of client accounts with credit balances that have been inactive for 30 calendar days; Automated or workflow-triggered payment initiation to return credit balance within three working days of the 30-day inactivity threshold being met; Exception report for any credit balances not returned within the three-working-day window

### SB-RUNACCT-008 — Use Date of Realisation as Settlement Date for Physical Payment Instruments
- **Clauses:** 47.5
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** Where a physical payment instrument (cheque or demand draft) is issued by the TM for settlement of a client's running account due to failure of electronic payment instructions, the settlement date shall be the date on which the instrument is realised into the client's bank account, not the date of issue of the instrument.
- **Expected controls:** Tracking mechanism to record the realisation date of physical payment instruments issued for running account settlements; System update to reflect settlement completion only upon confirmed realisation, not instrument issuance date; Reconciliation process to monitor outstanding physical instruments and follow up on realisation

### SB-RUNACCT-009 — Discontinue Retention of Funds for Administrative/Operational Difficulties for Active Clients
- **Clauses:** 47.6
- **Category:** client_funds_settlement · **Intermediary:** trading_member
- **Obligation:** The TM must discontinue retaining any client funds on grounds of administrative or operational difficulties in settling the accounts of regular trading (active) clients.
- **Expected controls:** Policy and procedural control explicitly prohibiting retention of active client funds for administrative/operational reasons; Periodic internal audit to confirm no such retention is occurring for active client accounts

### SB-RUNACCT-010 — Prohibit Authorized Person from Accepting Client Funds and Securities
- **Clauses:** 47.7
- **Category:** authorized_person_conduct · **Intermediary:** trading_member
- **Obligation:** Authorized Persons are not permitted to accept client funds or securities. The TM must maintain a proper check to enforce this prohibition. Proprietary trading by an Authorized Person is permitted only using the Authorized Person's own funds and securities, and not using any client funds.
- **Expected controls:** Written policy and contractual prohibition on Authorized Persons accepting client funds or securities; Periodic supervisory checks and reconciliation to detect any instance of an Authorized Person handling client funds; Controls to ensure Authorized Person proprietary trading accounts are funded solely from own funds, with system segregation from client fund flows

### SB-RUNACCT-011 — Send SMS and Email Intimation to Client Upon Running Account Settlement with Transfer Details
- **Clauses:** 47.8
- **Category:** client_communication · **Intermediary:** trading_member
- **Obligation:** Upon settling a client's running account, the TM must send an intimation to the client via SMS to the client's registered mobile number and by email. The intimation must include details of the fund transfer: for electronic transfers, the transaction number and date; for physical payment instruments, the instrument number and date. The TM must also send the retention statement along with the statement of running accounts to the client within 5 working days of settlement, as per existing provisions.
- **Expected controls:** Automated SMS and email dispatch system triggered at the time of running account settlement, containing transfer details (transaction/instrument number and date); Template-based intimation capturing electronic transfer or physical instrument details as applicable; System to generate and dispatch retention statement along with running account statement within 5 working days of settlement date; Delivery confirmation tracking and exception reporting for failed SMS/email intimations

### SB-RUNACCT-012 — Allow Client 30 Working Days to Raise Disputes on Running Account Statement
- **Clauses:** 47.9
- **Category:** client_communication · **Intermediary:** trading_member
- **Obligation:** A client must bring any dispute regarding the statement of running account to the notice of the TM within 30 working days from the date of the statement. The TM must maintain a process to receive, log, and address such disputes within this timeframe.
- **Expected controls:** Defined dispute-receipt channel (email, portal, or written communication) accessible to clients for running account statement disputes; Log or ticketing system to record date of receipt and track resolution of client disputes; Communication to clients informing them of the 30-working-day dispute window in the statement or accompanying communication

### SB-RUNACCT-013 — Cooperate with Stock Exchange Online Monitoring System for Running Account Settlement Compliance
- **Clauses:** 47.10
- **Category:** regulatory_reporting_and_monitoring · **Intermediary:** trading_member
- **Obligation:** Stock Exchanges shall develop an online monitoring system to verify timely settlement of clients' running accounts and to confirm that excess client funds are not retained by the TM as on the settlement date. The TM must ensure its records, data, and processes support and are compatible with this Exchange-operated monitoring mechanism, and must not retain excess client funds across all Exchanges after the settlement date.
- **Expected controls:** Systems capable of providing accurate, timely settlement and retention data to Stock Exchange online monitoring platforms; Internal compliance review on each settlement date to confirm no excess client funds are retained across all Exchanges; Escalation process for identifying and remediating any excess retention flagged by Exchange monitoring

## Relation edges (6)

- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/DOP/P/CIR/2021/577`  (chapter 47 footnote: dated June 16,2021)
- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/DOP/P/CIR/2022/101`  (chapter 47 footnote: dated July 27, 2022)
- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --consolidated_by--> `SEBI/HO/MIRSD/MIRSD-PoD1/P/CIR/2023/197`  (chapter 47 footnote: dated December 28, 2023)
- `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110` --supersedes--> `SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/53`  (successor master circular for stock brokers)
- `SEBI/HO/MIRSD/DOP/P/CIR/2022/101` --amends--> `SEBI/HO/MIRSD/DOP/P/CIR/2021/577`  (same-topic chronological amendment (running-account settlement))
- `SEBI/HO/MIRSD/MIRSD-PoD1/P/CIR/2023/197` --amends--> `SEBI/HO/MIRSD/DOP/P/CIR/2022/101`  (same-topic chronological amendment (running-account settlement))
