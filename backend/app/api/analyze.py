"""Scenario analysis endpoint — runs the full agent + synthesis pipeline."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from ..synthesis.synthesize import analyze_scenario

router = APIRouter(tags=["analyze"])


class AnalyzeRequest(BaseModel):
    scenario: str
    as_of: date | None = None


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    """Run the agentic pipeline: agent gathers applicable obligations -> synthesis emits cited findings.
    Returns findings + the full agent trajectory (for the trajectory viewer). Synchronous; ~30-60s."""
    return analyze_scenario(req.scenario, as_of=req.as_of)
