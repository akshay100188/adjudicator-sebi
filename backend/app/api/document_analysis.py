"""Document-upload analysis endpoint (WI-6, ADR-003 mode 2).

Accepts an uploaded policy/procedure document, extracts practice assertions, and runs the SAME
agent+synthesis engine the scenario path uses. PII posture (§3): the raw upload is processed in memory
and never persisted; only derived finding metadata is returned.

Not legal advice — for expert review only.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..ingest.document_adapter import analyse_document

router = APIRouter(tags=["analyze"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB — a policy doc is small; bound the ephemeral memory use


@router.post("/analyze/document")
async def analyze_document(file: UploadFile = File(...), as_of: date | None = Form(default=None)):
    """Upload a policy document -> extracted practice assertions -> cited gap findings.

    The raw upload is processed ephemerally in memory and never written to disk or persisted
    (`raw_document_persisted: false` in the response). Synchronous; ~30-60s.
    """
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty upload")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"file exceeds {MAX_UPLOAD_BYTES // (1024*1024)} MB limit")
    try:
        result = analyse_document(file.filename or "upload", raw, as_of=as_of)
    finally:
        del raw  # guarantee the raw bytes are dropped even on error (PII posture)
    return result
