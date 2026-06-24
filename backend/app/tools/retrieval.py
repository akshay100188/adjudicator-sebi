"""Phase 3 retrieval substrate — the tools the agent will call (T1-T4 here, T5 in rerank.py).

Each function is a clean, callable tool with a simple signature. Retrieval is recall-first:
over-return, then let rerank + the agent tighten. Knobs are explicit parameters so the eval
harness can sweep them (dense_k, sparse_k, rrf_k, ...).

One chunk per obligation in v1, so retrieval is reported at obligation grain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from ..db import get_cursor
from ..ingest.embed import embed_texts, to_pgvector


def _or_query(query: str) -> str:
    """Recall-first lexical query: OR the terms (websearch_to_tsquery is stopword-safe)."""
    tokens = re.findall(r"[A-Za-z0-9]+", query)
    return " OR ".join(tokens)


@dataclass
class Hit:
    obligation_id: str
    title: str
    score: float
    source: str  # "dense" | "sparse" | "hybrid"


# --- T1: temporal_filter (deterministic SQL; free) ----------------------------
def temporal_filter(as_of: date, family: str = "stock_brokers", include_synthetic: bool = False) -> set[str]:
    with get_cursor() as cur:
        cur.execute(
            "select obligation_id from adj_valid_obligations(%s, %s) "
            "where (%s or not is_synthetic);",
            (as_of, family, include_synthetic),
        )
        return {r["obligation_id"] for r in cur.fetchall()}


# --- T2 building blocks: dense + sparse, fused by RRF -------------------------
def embed_query(query: str) -> str:
    """Precompute a query's pgvector literal (cache across sweep configs to save embed cost)."""
    return to_pgvector(embed_texts([query])[0])


def dense_search(query: str, k: int = 10, allowed: set[str] | None = None, qv: str | None = None) -> list[Hit]:
    qv = qv or embed_query(query)
    sql = """
        select o.obligation_id, o.title, 1 - (c.embedding <=> %s::vector) as score
        from adj_obligation_chunk c join adj_obligation o using (obligation_id)
        where o.is_synthetic = false {flt}
        order by c.embedding <=> %s::vector
        limit %s;"""
    params: list = [qv]
    flt = ""
    if allowed is not None:
        flt = "and o.obligation_id = any(%s)"
        params.append(list(allowed))
    params += [qv, k]
    with get_cursor() as cur:
        cur.execute(sql.format(flt=flt), params)
        return [Hit(r["obligation_id"], r["title"], float(r["score"]), "dense") for r in cur.fetchall()]


def sparse_search(query: str, k: int = 10, allowed: set[str] | None = None) -> list[Hit]:
    """Lexical BM25-ish via Postgres FTS (ADR 3.3: native ts_rank first)."""
    oq = _or_query(query)
    sql = """
        select o.obligation_id, o.title,
               ts_rank_cd(c.tsv, websearch_to_tsquery('english', %s)) as score
        from adj_obligation_chunk c join adj_obligation o using (obligation_id)
        where o.is_synthetic = false
          and c.tsv @@ websearch_to_tsquery('english', %s) {flt}
        order by score desc
        limit %s;"""
    params: list = [oq, oq]
    flt = ""
    if allowed is not None:
        flt = "and o.obligation_id = any(%s)"
        params.append(list(allowed))
    params.append(k)
    with get_cursor() as cur:
        cur.execute(sql.format(flt=flt), params)
        return [Hit(r["obligation_id"], r["title"], float(r["score"]), "sparse") for r in cur.fetchall()]


def rrf_merge(rankings: list[list[Hit]], rrf_k: int = 60, top_k: int = 10) -> list[Hit]:
    """Reciprocal Rank Fusion: score(d) = sum 1/(rrf_k + rank_i(d)). Rank-based, scale-free."""
    fused: dict[str, float] = {}
    meta: dict[str, Hit] = {}
    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            fused[hit.obligation_id] = fused.get(hit.obligation_id, 0.0) + 1.0 / (rrf_k + rank)
            meta.setdefault(hit.obligation_id, hit)
    order = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [Hit(oid, meta[oid].title, score, "hybrid") for oid, score in order]


# --- T2: hybrid_search (the headline retrieval tool) -------------------------
def hybrid_search(
    query: str,
    dense_k: int = 10,
    sparse_k: int = 10,
    rrf_k: int = 60,
    top_k: int = 10,
    allowed: set[str] | None = None,
    qv: str | None = None,
) -> list[Hit]:
    d = dense_search(query, dense_k, allowed, qv=qv)
    s = sparse_search(query, sparse_k, allowed)
    return rrf_merge([d, s], rrf_k=rrf_k, top_k=top_k)


# --- T3: expand_to_parent ----------------------------------------------------
def expand_to_parent(obligation_id: str) -> dict | None:
    with get_cursor() as cur:
        cur.execute(
            """select s.section_id, s.heading, s.full_text, o.clause_refs
               from adj_obligation o join adj_obligation_section s on o.parent_section_id = s.section_id
               where o.obligation_id = %s;""",
            (obligation_id,),
        )
        return cur.fetchone()


# --- T4: graph_lookup (recursive citation-graph traversal) -------------------
def graph_lookup(circular_ref: str, rel_types: list[str] | None = None, max_depth: int = 10) -> list[dict]:
    rel = rel_types or ["supersedes", "amends", "consolidated_by", "refers_to"]
    with get_cursor() as cur:
        cur.execute(
            "select from_ref, to_ref, relation_type, depth "
            "from adj_relation_closure(%s, %s, %s) order by depth;",
            (circular_ref, rel, max_depth),
        )
        return [dict(r) for r in cur.fetchall()]
