"""Deterministic citation-graph edges (ADR-006). No LLM.

For a parsed chapter, the footnote source-circular references are the circulars the
chapter consolidates. We emit:
  - (master_ref) --consolidated_by--> (each source circular)   [from footnotes]
  - (master_ref) --supersedes-------> (prior master)           [from manifest]
  - chronological --amends--> edges between the source circulars on the same topic.

These edges seed adj_obligation_relations and are what tool T4 traverses. They are
proposed for human review (ADR-009) before load.
"""
from __future__ import annotations

from datetime import datetime

from .parse import ParsedChapter


def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.replace(",", ", ").replace("  ", " ").strip()
    for fmt in ("%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(" ".join(s.split()), fmt)
        except ValueError:
            continue
    return None


def build_edges(
    chapter: ParsedChapter,
    master_ref: str,
    prior_master_ref: str | None = None,
) -> list[dict]:
    edges: list[dict] = []

    # Master consolidates each cited source circular.
    for ref in chapter.source_refs:
        edges.append({
            "from_ref": master_ref,
            "to_ref": ref.circular_ref,
            "relation_type": "consolidated_by",
            "source_note": f"chapter {chapter.chapter_no} footnote: dated {ref.dated}",
        })

    # Master supersedes the prior master circular.
    if prior_master_ref:
        edges.append({
            "from_ref": master_ref,
            "to_ref": prior_master_ref,
            "relation_type": "supersedes",
            "source_note": "successor master circular for stock brokers",
        })

    # Chronological amends edges among the source circulars (later amends earlier).
    dated = [(r.circular_ref, _parse_date(r.dated)) for r in chapter.source_refs]
    dated = [(ref, d) for ref, d in dated if d is not None]
    dated.sort(key=lambda x: x[1])
    for (earlier, _), (later, _) in zip(dated, dated[1:]):
        edges.append({
            "from_ref": later,
            "to_ref": earlier,
            "relation_type": "amends",
            "source_note": "same-topic chronological amendment (running-account settlement)",
        })

    return edges
