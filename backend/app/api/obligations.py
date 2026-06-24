"""Obligation browser endpoints."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from ..db import get_cursor
from ..tools.retrieval import graph_lookup, temporal_filter

router = APIRouter(prefix="/obligations", tags=["obligations"])


@router.get("")
def list_obligations():
    valid = temporal_filter(date.today())
    with get_cursor() as cur:
        cur.execute(
            """select o.obligation_id, o.title, o.category, o.intermediary_type,
                      o.source_circular_ref, o.clause_refs, o.parent_section_id,
                      s.heading as chapter
               from adj_obligation o left join adj_obligation_section s
                 on o.parent_section_id = s.section_id
               where o.is_synthetic = false
               order by o.obligation_id;"""
        )
        rows = cur.fetchall()
    return [
        {**dict(r), "valid_today": r["obligation_id"] in valid}
        for r in rows
    ]


@router.get("/{obligation_id}")
def get_obligation(obligation_id: str):
    with get_cursor() as cur:
        cur.execute(
            """select o.*, s.heading as chapter, s.full_text as parent_text
               from adj_obligation o left join adj_obligation_section s
                 on o.parent_section_id = s.section_id
               where o.obligation_id = %s;""",
            (obligation_id,),
        )
        row = cur.fetchone()
    if not row:
        return {"error": "not found"}
    edges = graph_lookup(row["source_circular_ref"])
    return {**dict(row), "citation_graph": edges}
