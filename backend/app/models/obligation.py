"""Pydantic models mirroring the Phase 1 schema (adjudicator.adj_*)."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RelationType(str, Enum):
    amends = "amends"
    supersedes = "supersedes"
    refers_to = "refers_to"
    consolidated_by = "consolidated_by"


class ObligationSection(BaseModel):
    section_id: str
    circular_ref: str
    heading: Optional[str] = None
    full_text: str


class Obligation(BaseModel):
    obligation_id: str
    obligation_text: str
    source_circular_ref: str
    source_url: str
    issue_date: date
    effective_date: date
    superseded_by: Optional[str] = None
    regulation_family: str = "stock_brokers"
    intermediary_type: Optional[str] = None
    category: Optional[str] = None
    parent_section_id: Optional[str] = None
    is_synthetic: bool = False

    def valid_as_of(self, as_of: date, superseder_effective: Optional[date]) -> bool:
        """Temporal validity, mirroring adj_valid_obligations().

        superseder_effective: effective_date of the obligation named in
        superseded_by, or None if not superseded / superseder unknown.
        """
        if self.effective_date > as_of:
            return False
        if self.superseded_by is None:
            return True
        if superseder_effective is None:
            return True  # superseder not yet effective / not present
        return superseder_effective > as_of


class ObligationRelation(BaseModel):
    from_ref: str
    to_ref: str
    relation_type: RelationType
    source_note: Optional[str] = None


class ObligationChunk(BaseModel):
    chunk_id: str
    obligation_id: Optional[str] = None
    section_id: Optional[str] = None
    chunk_text: str
    context_blurb: Optional[str] = None
