"""T5: rerank. ADR 3.4 — benchmark Haiku (cheap, in-domain) first; cross-encoder later.

The reranker re-scores a recall-first candidate set for true relevance to the query.
Haiku reads (query, candidate obligation texts) and returns a relevance score per candidate.
"""
from __future__ import annotations

import json

import anthropic

from ..config import settings
from ..db import get_cursor
from .retrieval import Hit

MODEL = "claude-haiku-4-5-20251001"


def _texts_for(oids: list[str]) -> dict[str, str]:
    with get_cursor() as cur:
        cur.execute(
            "select obligation_id, title, obligation_text from adj_obligation "
            "where obligation_id = any(%s);",
            (oids,),
        )
        return {r["obligation_id"]: f"{r['title']}: {r['obligation_text']}" for r in cur.fetchall()}


def rerank(query: str, candidates: list[Hit], top_k: int = 5) -> list[Hit]:
    if not candidates:
        return []
    texts = _texts_for([h.obligation_id for h in candidates])
    listing = "\n".join(f"[{h.obligation_id}] {texts.get(h.obligation_id, h.title)}" for h in candidates)
    system = (
        "You are a retrieval reranker for SEBI stock-broker compliance. Given a user query and "
        "candidate obligations, score each 0.0-1.0 for how directly it answers/applies to the query. "
        "Return ONLY a JSON object mapping obligation_id -> score."
    )
    user = f"QUERY: {query}\n\nCANDIDATES:\n{listing}\n\nReturn the JSON score map now."
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=MODEL, max_tokens=800, system=system,
        messages=[{"role": "user", "content": user}],
    )
    txt = resp.content[0].text.strip()
    if txt.startswith("```"):
        txt = txt.split("```", 2)[1].lstrip("json").strip()
    scores = json.loads(txt)
    rescored = [Hit(h.obligation_id, h.title, float(scores.get(h.obligation_id, 0.0)), "rerank") for h in candidates]
    rescored.sort(key=lambda h: h.score, reverse=True)
    return rescored[:top_k]
