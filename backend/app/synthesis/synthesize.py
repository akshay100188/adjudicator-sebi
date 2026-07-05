"""Phase 5 — grounded synthesis: scenario + applicable obligations -> cited gap findings.

Sonnet compares the scenario's described practices against each obligation's expected controls and
emits a structured finding ONLY where there is a genuine gap. Grounding contract (ADR 5.2): it may
only cite obligations passed to it; we also filter in code. No phantom findings on compliant input
(the v1 lesson: no fallback that invents gaps).

Not legal advice — for expert review only.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date

import anthropic

from ..config import settings
from ..db import get_cursor
from ..agent.agent import DISCLAIMER, run_agent

MODEL = "claude-sonnet-4-6"

SYSTEM = """You are a SEBI stock-broker (Trading Member) compliance analyst. You are given a \
product-change SCENARIO and a set of currently-valid OBLIGATIONS (each with expected controls and a \
source citation). Find only the obligations the scenario ACTIVELY VIOLATES.

This is a gap detector, not a checklist. The obligation list is broad (recall-first); most of it will
NOT be violated. Be conservative — a false alarm manufactures false compliance risk.

Emit a finding for an obligation ONLY IF BOTH hold:
  (1) the SCENARIO contains a specific statement describing a practice, AND
  (2) that stated practice directly CONTRADICTS the obligation.
`evidence` MUST be that specific contradicting sentence/clause, quoted or closely paraphrased FROM THE
SCENARIO. If you cannot point to such a contradicting statement, DO NOT emit a finding.

SILENCE IS NOT A GAP. If the scenario does not mention a topic, emit nothing for it.
COMPLIANCE IS NOT A GAP. If the scenario's stated practice satisfies the obligation, emit nothing.
A scenario that describes good practice throughout must yield an EMPTY array.

You may ONLY cite obligation_ids from the provided list. Never invent obligations or citations.
This is NOT legal advice; you surface potential gaps for expert review.

Return ONLY a JSON array (possibly empty) of objects:
  {"obligation_id","gap_summary","evidence","recommended_action","confidence":"high|medium|low"}"""


@dataclass
class Finding:
    obligation_id: str
    gap_summary: str
    evidence: str
    recommended_action: str
    confidence: str
    citation: str  # filled from the obligation's real source (not from the LLM)


def _fetch(obligation_ids: list[str]) -> dict[str, dict]:
    if not obligation_ids:
        return {}
    with get_cursor() as cur:
        cur.execute(
            """select obligation_id, title, obligation_text, expected_controls,
                      source_circular_ref, clause_refs
               from adj_obligation where obligation_id = any(%s);""",
            (obligation_ids,),
        )
        return {r["obligation_id"]: dict(r) for r in cur.fetchall()}


def synthesize(scenario: str, obligations: dict[str, dict]) -> list[Finding]:
    if not obligations:
        return []
    block = "\n\n".join(
        f"[{oid}] {o['title']}\nRequirement: {o['obligation_text']}\n"
        f"Expected controls: {'; '.join(o.get('expected_controls') or [])}"
        for oid, o in obligations.items()
    )
    user = f"SCENARIO:\n{scenario}\n\nOBLIGATIONS:\n{block}\n\nReturn the findings JSON array now."
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=MODEL, max_tokens=2500,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    txt = resp.content[0].text.strip()
    if "```" in txt:
        txt = txt.split("```")[1].lstrip("json").strip()
    s, e = txt.find("["), txt.rfind("]")
    raw = json.loads(txt[s:e + 1]) if s >= 0 and e > s else []

    findings: list[Finding] = []
    for f in raw:
        oid = f.get("obligation_id")
        if oid not in obligations:  # grounding gate
            continue
        o = obligations[oid]
        cite = f"{o['source_circular_ref']} (clause {', '.join(o.get('clause_refs') or [])})"
        findings.append(Finding(
            obligation_id=oid, gap_summary=f.get("gap_summary", ""), evidence=f.get("evidence", ""),
            recommended_action=f.get("recommended_action", ""), confidence=f.get("confidence", "medium"),
            citation=cite,
        ))
    return findings


# --- EXP-006: second-pass adjudication (precision pass, ADR-017 §3) --------------------------------
# The first synthesis pass is recall-first and over-flags: it emits a finding whenever a stated practice
# looks like a gap. This second pass re-examines EACH proposed finding in isolation and drops the ones
# that are "merely topically related" rather than a real violation of a binding requirement — the
# false-positive mode measured in EXP-005 (precision 0.76). It can only DROP findings, never add, so it
# cannot introduce a hallucination; the hard constraint is that it must not drop a true gap (recall 1.00).
ADJUDICATE_SYSTEM = """You are a STRICT second reviewer auditing proposed SEBI stock-broker compliance \
findings for false positives. For each proposed finding you are given the obligation's binding \
requirement and the evidence sentence the first reviewer quoted from the scenario.

KEEP a finding ONLY IF the quoted evidence is a specific stated practice that DIRECTLY VIOLATES a \
binding requirement of that obligation — i.e. doing what the scenario says would breach the obligation.

DROP a finding if ANY of these hold:
  - the obligation is merely TOPICALLY RELATED (same subject area) but the scenario does not actually
    contradict its requirement;
  - the violation is INFERRED or ASSUMED rather than stated in the evidence;
  - the evidence describes a practice that is actually COMPLIANT with, or silent on, the requirement;
  - the same underlying practice is already captured by a more directly-violated obligation.

Be conservative about KEEPING but do NOT drop a finding that is a genuine, directly-evidenced violation
— a dropped true gap is the worst error. Return ONLY a JSON object mapping each obligation_id to
{"keep": true|false, "reason": "<one clause>"}."""


def adjudicate(scenario: str, findings: list[Finding], obligations: dict[str, dict]
               ) -> tuple[list[Finding], list[dict]]:
    """Re-examine each proposed finding; return (kept, rejected). Rejected entries carry a drop reason."""
    if len(findings) <= 0:
        return findings, []
    block = "\n\n".join(
        f"[{f.obligation_id}] REQUIREMENT: {obligations[f.obligation_id]['obligation_text']}\n"
        f"EVIDENCE (from scenario): {f.evidence}\nPROPOSED GAP: {f.gap_summary}"
        for f in findings if f.obligation_id in obligations
    )
    user = (f"SCENARIO:\n{scenario}\n\nPROPOSED FINDINGS TO AUDIT:\n{block}\n\n"
            "Return the keep/drop JSON object now.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=MODEL, max_tokens=1500,
        system=[{"type": "text", "text": ADJUDICATE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    txt = resp.content[0].text.strip()
    if "```" in txt:
        txt = txt.split("```")[1].lstrip("json").strip()
    s, e = txt.find("{"), txt.rfind("}")
    try:
        verdicts = json.loads(txt[s:e + 1]) if s >= 0 and e > s else {}
    except json.JSONDecodeError:
        verdicts = {}

    kept: list[Finding] = []
    rejected: list[dict] = []
    for f in findings:
        v = verdicts.get(f.obligation_id)
        # Fail-safe: if the adjudicator returns no verdict for a finding, KEEP it (protect recall).
        if v is None or v.get("keep", True):
            kept.append(f)
        else:
            rejected.append({"obligation_id": f.obligation_id, "gap_summary": f.gap_summary,
                             "reason": v.get("reason", "dropped as merely topically related")})
    return kept, rejected


def analyze_scenario(scenario: str, as_of: date | None = None, adjudicate_pass: bool = True) -> dict:
    """Full pipeline: agent gathers applicable obligations -> synthesis emits cited gap findings.

    `adjudicate_pass` runs the EXP-006 second-pass precision review that drops merely-topical findings;
    dropped candidates are returned in `rejected_findings` so the precision decision is auditable.
    """
    agent = run_agent(scenario, as_of=as_of)
    obligations = _fetch(agent.relevant_obligations)
    findings = synthesize(scenario, obligations)
    rejected: list[dict] = []
    if adjudicate_pass:
        findings, rejected = adjudicate(scenario, findings, obligations)
    return {
        "route": agent.route,
        "reasoning": agent.reasoning,
        "obligations_considered": [
            {"obligation_id": oid, "title": o["title"]} for oid, o in obligations.items()
        ],
        "findings": [asdict(f) for f in findings],
        "rejected_findings": rejected,
        "trajectory": [
            {"step": i + 1, "tool": s.tool, "args": s.args, "observation": s.observation}
            for i, s in enumerate(agent.trajectory)
        ],
        "trajectory_tools": agent.tool_sequence(),
        "grounding_dropped": agent.grounding_dropped,
        "steps_used": agent.steps_used,
        "disclaimer": DISCLAIMER,
    }
