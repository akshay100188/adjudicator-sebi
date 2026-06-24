"""Adjudicator (SEBI) API — exposes the agentic engine for the Next.js UI.

Not legal advice. Every analysis carries a non-removable disclaimer.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analyze, obligations

app = FastAPI(title="Project Adjudicator (SEBI) — Agentic RAG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(obligations.router)
app.include_router(analyze.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "adjudicator-sebi", "note": "prototype — not legal advice"}
