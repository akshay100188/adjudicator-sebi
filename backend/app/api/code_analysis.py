"""Code-analysis endpoint (Phase 8 stretch). Privacy-safe: code is never stored or sent to the LLM."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ..code_scan.analyse import analyse_github, analyse_path

router = APIRouter(prefix="/code-analysis", tags=["code-analysis"])


class CodeRequest(BaseModel):
    repo_path: str | None = None
    github_url: str | None = None


@router.post("/analyse")
def analyse(req: CodeRequest):
    """Scan a repo for compliance-relevant signals and map them to SEBI obligations.
    Provide repo_path (local) or github_url (shallow-cloned then deleted). ~30-60s."""
    if req.github_url:
        return analyse_github(req.github_url)
    if req.repo_path:
        return analyse_path(req.repo_path)
    return {"error": "provide repo_path or github_url"}
