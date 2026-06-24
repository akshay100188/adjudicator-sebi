# ADR-018: Code-analysis module (Phase 8 stretch)

Status: accepted
Date: 2026-06-25
Plan ref: Phase 8, §3 (PII), ADR-005

## Context
The differentiator: map a code repository to SEBI obligations. ADR-005 kept this out of v1 core; it is
built here as a stretch only after the agent + eval were solid, and must not compromise the privacy
posture (§3).

## Decisions
1. **Signals, not code.** The scanner extracts *signals* — file path, line, category, short
   description — and never retains or transmits the source. `del text` after each file; only metadata
   flows downstream. GitHub repos: shallow clone → scan → `rmtree` (code never persisted).
2. **Three layers, graceful.** Regex pattern rules (any language) + a Python-AST layer (fund-movement
   functions missing an audit-trail call). Semgrep is an optional third layer — absent here, so the
   scanner degrades gracefully to regex+AST (no hard dependency).
3. **Reuse the engine.** Signals are rendered into a practice description and fed to the SAME
   `analyze_scenario()` pipeline (agent → synthesis). The agent maps signals to obligations via
   retrieval; synthesis emits cited findings. No bespoke code→obligation map — the agentic core does it.
4. **Honesty about coverage.** Most SEBI stock-broker obligations are process/governance, not code
   patterns; the scanner only surfaces the code-detectable subset (fund pooling, settlement cadence,
   audit trail, PII logging, secrets, AP fund handling). This is a demonstrated capability, not full
   coverage — stated plainly.

## Why
The privacy posture is the whole reason a compliance tool is procurable; "signals not code" makes the
module safe by construction. Reusing the agent+synthesis engine keeps the architecture coherent and
avoids a parallel code→obligation mapping that would rot.

## Consequences / what we'll measure
- `backend/app/code_scan/` (scanner, analyse); `POST /code-analysis/analyse`.
- Demo: `data/code_samples/broking_app/` (synthetic, intentionally non-compliant) → 9 signals →
  cited obligation findings (settlement cadence, fund pooling/upstreaming, PII, etc.).
- Future: add the Semgrep layer + a small gold set of (repo → expected obligations) for a code-finding
  P/R metric, mirroring the scenario eval.
