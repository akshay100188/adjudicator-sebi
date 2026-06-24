"""LLM-assisted obligation extraction (ADR-009: hybrid, human reviews the output).

Claude reads the parsed chapter clauses and proposes normalized, self-contained
obligations, each anchored to the clause number(s) it derives from (grounding). The
output is written to a review file for human approval — it is NOT loaded automatically.

Grounding contract: every obligation must map to clause_refs that exist in the chapter;
the model must not invent requirements not present in the text.
"""
from __future__ import annotations

import json

import anthropic

from ..config import settings
from .parse import ParsedChapter

MODEL = "claude-sonnet-4-6"

SYSTEM = """You are a regulatory analyst extracting structured compliance obligations \
from official SEBI circular text for a stock-broker (Trading Member) compliance tool.

Rules:
- Extract DISTINCT, self-contained obligations. Merge a header clause with its sub-clauses \
only when they express one requirement; otherwise keep them separate.
- Every obligation MUST cite the clause number(s) it derives from in `clause_refs`. Only use \
clause numbers that appear in the provided text. Do NOT invent requirements.
- `obligation_text` must be a faithful, self-contained paraphrase a compliance officer can act on \
(resolve pronouns like "such account"). Stay true to the source; do not add scope.
- `expected_controls` = concrete, checkable controls a firm must have to satisfy the obligation \
(used later for gap detection). 1-4 short items.
- This is NOT legal advice; you are structuring text for expert review.

Return ONLY valid JSON: an array of objects with keys:
  suggested_id (string, e.g. "SB-RUNACCT-001"; SB = stock broker, short topic slug, zero-padded),
  title (short),
  clause_refs (array of strings),
  obligation_text (string),
  category (string snake_case, e.g. "client_funds_settlement"),
  intermediary_type (string, usually "trading_member"),
  expected_controls (array of strings)."""


def extract_obligations(chapter: ParsedChapter) -> list[dict]:
    clause_block = "\n".join(f"[{c.clause_no}] {c.text}" for c in chapter.clauses)
    user = (
        f"Chapter {chapter.chapter_no}: {chapter.heading}\n"
        f"Source circulars consolidated: "
        f"{', '.join(r.circular_ref for r in chapter.source_refs)}\n\n"
        f"CLAUSES:\n{clause_block}\n\n"
        "Extract the obligations as a JSON array now."
    )
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8000,  # large chapters (e.g. ch17) produce long JSON; avoid truncation
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    if resp.stop_reason == "max_tokens":
        raise RuntimeError(f"extraction truncated at max_tokens for chapter {chapter.chapter_no}")
    text = resp.content[0].text.strip()
    # Strip markdown fences if present.
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    return json.loads(text)
