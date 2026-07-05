"""EXP-008 — embedding bake-off (ADR-004 re-examination, WI-7).

Benchmarks the v1 baseline `text-embedding-3-small` @ 512-dim against `text-embedding-3-large` at
512 and 1024 dims on golden dense recall@k. Runs entirely in memory (embed corpus + queries fresh,
cosine similarity in numpy) so it never touches the production `adj_obligation_chunk.embedding`
column or the pgvector schema. Re-embedding to actually swap models is a one-time cost (ADR-004).

Dense-only comparison on purpose: the embedding model is a dense-retrieval knob, so we isolate it
from rerank/hybrid. Keep/revert on golden recall@k.

Usage:  python scripts/run_embedding_bakeoff.py
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import openai

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.config import settings          # noqa: E402
from app.db import get_cursor            # noqa: E402
from eval.harness import load_golden, recall_at_k  # noqa: E402

KS = (1, 3, 5)
CONFIGS = [
    ("text-embedding-3-small", 512),   # v1 baseline (ADR-004)
    ("text-embedding-3-large", 512),   # same storage cost, stronger model
    ("text-embedding-3-large", 1024),  # more headroom (2x storage)
]
REPORTS = ROOT / "docs" / "experiments"


def load_corpus() -> tuple[list[str], list[str]]:
    """Chunk texts + their obligation ids (one chunk per obligation in v1)."""
    with get_cursor() as cur:
        cur.execute(
            "select o.obligation_id, c.chunk_text "
            "from adj_obligation_chunk c join adj_obligation o using (obligation_id) "
            "where o.is_synthetic = false order by o.obligation_id;"
        )
        rows = cur.fetchall()
    return [r["obligation_id"] for r in rows], [r["chunk_text"] for r in rows]


def embed(client, model: str, dims: int, texts: list[str]) -> np.ndarray:
    out: list[list[float]] = []
    for i in range(0, len(texts), 100):  # batch
        resp = client.embeddings.create(model=model, input=texts[i:i + 100], dimensions=dims)
        out.extend(d.embedding for d in resp.data)
    v = np.asarray(out, dtype=np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-9  # normalise -> cosine == dot
    return v


def evaluate(qvecs: np.ndarray, cvecs: np.ndarray, oids: list[str], queries) -> dict[int, float]:
    sims = qvecs @ cvecs.T  # (nq, ncorpus)
    rec = {k: 0.0 for k in KS}
    for i, q in enumerate(queries):
        order = np.argsort(-sims[i])
        ranked = [oids[j] for j in order]
        for k in KS:
            rec[k] += recall_at_k(q.expected, ranked, k)
    return {k: rec[k] / len(queries) for k in KS}


def main() -> int:
    queries = load_golden()
    oids, texts = load_corpus()
    client = openai.OpenAI(api_key=settings.openai_api_key)
    print(f"Embedding bake-off — {len(queries)} golden queries, {len(oids)} obligations (dense-only)\n")

    results = []
    for model, dims in CONFIGS:
        cvecs = embed(client, model, dims, texts)
        qvecs = embed(client, model, dims, [q.query for q in queries])
        rec = evaluate(qvecs, cvecs, oids, queries)
        results.append((model, dims, rec))
        print(f"  {model} @ {dims}d:  recall@1/3/5 = "
              f"{rec[1]:.2f} / {rec[3]:.2f} / {rec[5]:.2f}")

    base = results[0][2]
    lines = [
        f"# EXP-008: Embedding bake-off — text-embedding-3-small vs -3-large ({date.today().isoformat()})",
        "", "Related ADR: ADR-004 (embedding model). Plan ref: WI-7.",
        f"Dense-only recall@k on {len(queries)} golden queries, {len(oids)} obligations. In-memory "
        "(numpy cosine); production embeddings untouched.", "",
        "## Hypothesis",
        "A stronger embedding model (`-3-large`) lifts dense recall enough on this corpus to justify a "
        "one-time re-embed. Recall-first: the metric that matters is recall@k.", "",
        "## Results (dense recall@k, cosine)",
        "| model | dims | recall@1 | recall@3 | recall@5 | Δ recall@5 vs baseline |",
        "|---|---|---|---|---|---|",
    ]
    for model, dims, rec in results:
        tag = " *(baseline)*" if (model, dims) == ("text-embedding-3-small", 512) else ""
        lines.append(f"| {model}{tag} | {dims} | {rec[1]:.2f} | {rec[3]:.2f} | {rec[5]:.2f} "
                     f"| {rec[5] - base[5]:+.2f} |")
    lines += ["", "## Verdict", "TODO_VERDICT", ""]

    (REPORTS / "EXP-008-embedding-bakeoff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n  baseline (3-small@512) recall@5 = {base[5]:.2f}")
    print(f"  report -> docs/experiments/EXP-008-embedding-bakeoff.md (fill in the verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
