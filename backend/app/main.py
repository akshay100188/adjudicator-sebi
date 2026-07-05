"""Adjudicator (SEBI) API — exposes the agentic engine for the Next.js UI.

Not legal advice. Every analysis carries a non-removable disclaimer.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analyze, code_analysis, document_analysis, obligations

app = FastAPI(title="Project Adjudicator (SEBI) — Agentic RAG", version="0.1.0")

# CORS_ORIGINS: comma-separated allowed origins, or "*" (default). Set to the Vercel URL in prod.
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(obligations.router)
app.include_router(analyze.router)
app.include_router(document_analysis.router)
app.include_router(code_analysis.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "adjudicator-sebi", "note": "prototype — not legal advice"}
