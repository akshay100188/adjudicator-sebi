"""OpenAI embeddings (ADR-004: text-embedding-3-small @ 512 dims)."""
from __future__ import annotations

import openai

from ..config import settings

MODEL = "text-embedding-3-small"
DIMS = 512


def embed_texts(texts: list[str]) -> list[list[float]]:
    client = openai.OpenAI(api_key=settings.openai_api_key)
    resp = client.embeddings.create(model=MODEL, input=texts, dimensions=DIMS)
    return [d.embedding for d in resp.data]


def to_pgvector(vec: list[float]) -> str:
    """pgvector text literal: [0.1,0.2,...]."""
    return "[" + ",".join(f"{x:.7f}" for x in vec) + "]"
