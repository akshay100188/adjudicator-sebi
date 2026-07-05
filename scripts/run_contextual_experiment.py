"""EXP-007 — Contextual Retrieval on/off (ADR-010, WI-7).

Anthropic's Contextual Retrieval: before embedding, prepend a short LLM-generated blurb that situates
each chunk in its parent circular ("such person shall…" → which person, which obligation). We measure
our own recall@k lift rather than assuming it (the project's no-blind-knob rule).

Runs in memory (generate blurbs with Haiku, embed chunk-alone vs blurb+chunk with the same
`text-embedding-3-small` @ 512, cosine recall in numpy); the production `context_blurb` column and
embeddings are untouched. Keep/revert on the golden recall@k number.

Usage:  python scripts/run_contextual_experiment.py
"""
import sys
from datetime import date
from pathlib import Path

import anthropic
import numpy as np
import openai

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.config import settings          # noqa: E402
from app.db import get_cursor            # noqa: E402
from app.ingest.embed import MODEL as EMBED_MODEL, DIMS  # noqa: E402
from eval.harness import load_golden, recall_at_k        # noqa: E402

KS = (1, 3, 5)
BLURB_MODEL = "claude-haiku-4-5-20251001"
REPORTS = ROOT / "docs" / "experiments"

BLURB_SYSTEM = (
    "You situate a clause from a SEBI stock-broker master circular within its parent section, so the "
    "clause can be retrieved out of context. Given the SECTION and the CHUNK, write ONE short sentence "
    "(<=40 words) stating what obligation/topic the chunk belongs to and who it binds. Output only that "
    "sentence — no preamble."
)


def load_corpus():
    with get_cursor() as cur:
        cur.execute(
            """select o.obligation_id, c.chunk_text, s.heading, s.full_text
               from adj_obligation o
               join adj_obligation_chunk c using (obligation_id)
               join adj_obligation_section s on s.section_id = o.parent_section_id
               where not o.is_synthetic order by o.obligation_id;"""
        )
        return cur.fetchall()


def make_blurb(client, heading: str, parent: str, chunk: str) -> str:
    user = (f"SECTION HEADING: {heading}\nSECTION (context):\n{parent[:3500]}\n\n"
            f"CHUNK:\n{chunk}\n\nWrite the one-sentence situating context now.")
    resp = client.messages.create(
        model=BLURB_MODEL, max_tokens=120, system=BLURB_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip().replace("\n", " ")


def embed(client, texts):
    out = []
    for i in range(0, len(texts), 100):
        resp = client.embeddings.create(model=EMBED_MODEL, input=texts[i:i + 100], dimensions=DIMS)
        out.extend(d.embedding for d in resp.data)
    v = np.asarray(out, dtype=np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-9
    return v


def recall(qvecs, cvecs, oids, queries):
    sims = qvecs @ cvecs.T
    rec = {k: 0.0 for k in KS}
    for i, q in enumerate(queries):
        ranked = [oids[j] for j in np.argsort(-sims[i])]
        for k in KS:
            rec[k] += recall_at_k(q.expected, ranked, k)
    return {k: rec[k] / len(queries) for k in KS}


def main() -> int:
    queries = load_golden()
    rows = load_corpus()
    oids = [r["obligation_id"] for r in rows]
    chunks = [r["chunk_text"] for r in rows]

    a_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    o_client = openai.OpenAI(api_key=settings.openai_api_key)

    print(f"Contextual Retrieval on/off — {len(queries)} queries, {len(oids)} obligations, "
          f"embed={EMBED_MODEL}@{DIMS}\n  generating {len(rows)} context blurbs (Haiku)...")
    blurbs = [make_blurb(a_client, r["heading"] or "", r["full_text"] or "", r["chunk_text"]) for r in rows]
    contextual = [f"{b}\n{c}" for b, c in zip(blurbs, chunks)]

    qvecs = embed(o_client, [q.query for q in queries])
    off = recall(qvecs, embed(o_client, chunks), oids, queries)
    on = recall(qvecs, embed(o_client, contextual), oids, queries)

    print(f"  contextual OFF (chunk only):     recall@1/3/5 = {off[1]:.2f}/{off[3]:.2f}/{off[5]:.2f}")
    print(f"  contextual ON  (blurb + chunk):  recall@1/3/5 = {on[1]:.2f}/{on[3]:.2f}/{on[5]:.2f}")

    lines = [
        f"# EXP-007: Contextual Retrieval on/off ({date.today().isoformat()})",
        "", "Related ADR: ADR-010 (contextual retrieval). Plan ref: WI-7.",
        f"Dense recall@k, {len(queries)} golden queries, {len(oids)} obligations, "
        f"{EMBED_MODEL}@{DIMS}. In-memory; production embeddings untouched.", "",
        "## Hypothesis",
        "Prepending an LLM blurb that situates each clause in its parent section lifts dense recall by "
        "disambiguating context-dependent clauses (\"such person shall…\").", "",
        "## Sample blurb",
        f"> {blurbs[0]}", "",
        "## Results (dense recall@k)",
        "| config | recall@1 | recall@3 | recall@5 |",
        "|---|---|---|---|",
        f"| contextual OFF (chunk only) | {off[1]:.2f} | {off[3]:.2f} | {off[5]:.2f} |",
        f"| contextual ON (blurb + chunk) | {on[1]:.2f} | {on[3]:.2f} | {on[5]:.2f} |",
        f"| **delta** | {on[1]-off[1]:+.2f} | {on[3]-off[3]:+.2f} | {on[5]-off[5]:+.2f} |",
        "", "## Verdict", "TODO_VERDICT", "",
    ]
    (REPORTS / "EXP-007-contextual-retrieval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n  report -> docs/experiments/EXP-007-contextual-retrieval.md (fill in the verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
