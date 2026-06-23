# The 3-Point Checklist (cleared up front)

This is the competition / legal / PII clearance the project must satisfy. Locked in Phase 0.

## 1. Competition
Heavyweight licensed RegTech (Thomson Reuters Regulatory Intelligence, Wolters Kluwer OneSumX,
ComplyAdvantage; India-side Signzy / IRIS for filings). A **public, non-commercial showcase is not
in this market**. Referencing the landscape correctly signals understanding of it. **No competitive
exposure.**

## 2. Legal
SEBI circulars and master circulars are **public** (sebi.gov.in → *Legal*). Summarising and citing
them **non-commercially** is low-risk. Guardrails:
1. **Non-commercial** use only.
2. **Do not redistribute the corpus** as a standalone "database product."
3. ***Not legal advice / expert review only*** disclaimer on **every** finding (non-removable).
4. **Always link back to the source circular.**

## 3. PII
Minimal by design. Public corpus = no PII. The only PII risk is in **uploaded documents** (Phase 1b /
ADR-003) — an internal policy doc may contain names/data. Handling:
- Process **ephemerally**; **never persist the raw upload**.
- Store only **derived finding metadata**.
- **No third-party sharing.**
- If Phase 8 (code) is built: shallow clone → scan → delete; persist only finding metadata
  (file path, line, obligation code), never the code or the upload.

## Standing disclaimer (applied to every finding)
> This output does not constitute legal advice or a compliance determination. All findings require
> review by a qualified compliance professional. Always verify against the cited source circular.
