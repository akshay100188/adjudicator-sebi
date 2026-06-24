"""Anthropic tool-use schemas for the agent + dispatch to the Phase 3 tools.

Fine-grained tools (ADR 4.3) so the trajectory cleanly shows tool selection. Each dispatch
returns compact JSON-serialisable output (token discipline) and the obligation IDs it surfaced
(used by the grounding gate).
"""
from __future__ import annotations

from datetime import date

from ..db import get_cursor
from ..tools import retrieval as R
from ..tools.rerank import rerank as _rerank

TOOL_SCHEMAS = [
    {
        "name": "temporal_filter",
        "description": "Return the SEBI stock-broker obligations that are currently VALID as of a date "
                       "(effective and not superseded). Use to scope the universe before/after retrieval. "
                       "Deterministic; free.",
        "input_schema": {
            "type": "object",
            "properties": {"as_of": {"type": "string", "description": "ISO date YYYY-MM-DD; defaults to today"}},
        },
    },
    {
        "name": "hybrid_search",
        "description": "Recall-first hybrid search (dense embeddings + lexical, RRF-fused) over obligations. "
                       "Returns candidate obligations for a query. Call again with a reformulated, canonical "
                       "SEBI query if results look weak (corrective retrieval).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "description": "default 10"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "rerank",
        "description": "Re-score candidate obligations for true relevance to the query (precision). "
                       "Pass the query and a list of obligation_ids from hybrid_search.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "candidate_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["query", "candidate_ids"],
        },
    },
    {
        "name": "expand_to_parent",
        "description": "Get the full obligation text, its source circular reference, clause refs, parent "
                       "section, and any RELATED obligations it cross-references (shared defined terms like "
                       "USCNBA). Use before citing, to get the circular_ref for graph_lookup, and to follow "
                       "cross-references to related obligations in other chapters.",
        "input_schema": {
            "type": "object",
            "properties": {"obligation_id": {"type": "string"}},
            "required": ["obligation_id"],
        },
    },
    {
        "name": "graph_lookup",
        "description": "Traverse the citation graph from a circular reference: returns amends / supersedes / "
                       "consolidated_by / refers_to edges (with depth). Use for supersession / 'what changed' "
                       "/ 'consolidated position' questions.",
        "input_schema": {
            "type": "object",
            "properties": {"circular_ref": {"type": "string"}},
            "required": ["circular_ref"],
        },
    },
]


def dispatch(name: str, args: dict) -> tuple[dict, list[str]]:
    """Run a tool. Returns (observation_json, obligation_ids_surfaced)."""
    if name == "temporal_filter":
        as_of = date.fromisoformat(args["as_of"]) if args.get("as_of") else date.today()
        ids = sorted(R.temporal_filter(as_of))
        return {"as_of": str(as_of), "valid_count": len(ids), "valid_obligation_ids": ids}, ids

    if name == "hybrid_search":
        hits = R.hybrid_search(args["query"], top_k=int(args.get("top_k", 10)))
        items = [{"obligation_id": h.obligation_id, "title": h.title} for h in hits]
        return {"results": items}, [h.obligation_id for h in hits]

    if name == "rerank":
        cands = [R.Hit(oid, "", 0.0, "hybrid") for oid in args["candidate_ids"]]
        hits = _rerank(args["query"], cands, top_k=min(5, len(cands)))
        items = [{"obligation_id": h.obligation_id, "title": h.title, "score": round(h.score, 3)} for h in hits]
        return {"reranked": items}, [h.obligation_id for h in hits]

    if name == "expand_to_parent":
        oid = args["obligation_id"]
        with get_cursor() as cur:
            cur.execute(
                """select o.obligation_id, o.title, o.obligation_text, o.source_circular_ref,
                          o.clause_refs, s.heading as parent_heading
                   from adj_obligation o left join adj_obligation_section s
                     on o.parent_section_id = s.section_id
                   where o.obligation_id = %s;""",
                (oid,),
            )
            row = cur.fetchone()
        if not row:
            return {"error": "not found"}, []
        related = R.related_obligations(oid)
        out = {**dict(row), "related_obligations": related}
        surfaced = [oid] + [r["obligation_id"] for r in related]  # related obligations are grounded too
        return out, surfaced

    if name == "graph_lookup":
        edges = R.graph_lookup(args["circular_ref"])
        return {"edges": edges}, []

    return {"error": f"unknown tool {name}"}, []
