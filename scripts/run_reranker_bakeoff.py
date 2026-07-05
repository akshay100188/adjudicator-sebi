"""EXP-009 — reranker bake-off: Haiku (incumbent) vs a cross-encoder (ADR-014 re-examination, WI-7).

ADR-014 pinned Haiku as the reranker (MRR 0.97, reasons in-domain) and named a dedicated cross-encoder
as "a reasonable future comparison." This runs it: over the golden queries, take the same hybrid pool
of 10 the agent uses, rerank to top-5 with (a) Haiku and (b) a cross-encoder, and compare
MRR / precision@1 / recall@{1,3,5} and latency. Only switch on a measured win (Haiku is the incumbent).

Cross-encoder: `cross-encoder/ms-marco-MiniLM-L-6-v2` (small, local, ~80 MB; downloaded on first run).
If sentence-transformers or the model is unavailable, the script reports the Haiku baseline and records
the cross-encoder arm as deferred rather than fabricating a number.

Usage:  python scripts/run_reranker_bakeoff.py
"""
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.tools import retrieval as R                       # noqa: E402
from app.tools.rerank import rerank as haiku_rerank        # noqa: E402
from app.tools.rerank import _texts_for                    # noqa: E402
from eval.harness import (load_golden, recall_at_k, precision_at_k,  # noqa: E402
                          reciprocal_rank)

POOL, RRF, TOP_K, KS = 10, 60, 5, (1, 3, 5)
CE_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
REPORTS = ROOT / "docs" / "experiments"


def _metrics(name, ranked_lists, queries, latency_ms):
    rec = {k: sum(recall_at_k(q.expected, r, k) for q, r in zip(queries, ranked_lists)) / len(queries)
           for k in KS}
    p1 = sum(precision_at_k(q.expected, r, 1) for q, r in zip(queries, ranked_lists)) / len(queries)
    mrr = sum(reciprocal_rank(q.expected, r) for q, r in zip(queries, ranked_lists)) / len(queries)
    return {"name": name, "recall": rec, "p1": p1, "mrr": mrr, "latency": latency_ms}


def main() -> int:
    queries = load_golden()
    qv = {q.id: R.embed_query(q.query) for q in queries}
    pools = {q.id: R.hybrid_search(q.query, POOL, POOL, RRF, POOL, qv=qv[q.id]) for q in queries}
    print(f"Reranker bake-off — {len(queries)} golden queries, hybrid pool={POOL} -> top-{TOP_K}\n")

    # --- Haiku (incumbent) ---
    haiku_ranked, t0 = [], time.perf_counter()
    for q in queries:
        haiku_ranked.append([h.obligation_id for h in haiku_rerank(q.query, pools[q.id], top_k=TOP_K)])
    haiku = _metrics("Haiku (incumbent)", haiku_ranked, queries, (time.perf_counter() - t0) * 1000 / len(queries))
    print(f"  Haiku:         MRR {haiku['mrr']:.2f}  P@1 {haiku['p1']:.2f}  "
          f"recall@1/3/5 {haiku['recall'][1]:.2f}/{haiku['recall'][3]:.2f}/{haiku['recall'][5]:.2f}  "
          f"{haiku['latency']:.0f} ms/q")

    # --- Cross-encoder ---
    ce = None
    ce_error = None
    try:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder(CE_MODEL)
        texts = {}
        for q in queries:
            texts.update(_texts_for([h.obligation_id for h in pools[q.id]]))
        ce_ranked, t0 = [], time.perf_counter()
        for q in queries:
            cands = pools[q.id]
            pairs = [(q.query, texts.get(h.obligation_id, h.title)) for h in cands]
            scores = model.predict(pairs)
            order = sorted(zip(cands, scores), key=lambda x: x[1], reverse=True)[:TOP_K]
            ce_ranked.append([h.obligation_id for h, _ in order])
        ce = _metrics(f"Cross-encoder ({CE_MODEL.split('/')[-1]})", ce_ranked, queries,
                      (time.perf_counter() - t0) * 1000 / len(queries))
        print(f"  Cross-encoder: MRR {ce['mrr']:.2f}  P@1 {ce['p1']:.2f}  "
              f"recall@1/3/5 {ce['recall'][1]:.2f}/{ce['recall'][3]:.2f}/{ce['recall'][5]:.2f}  "
              f"{ce['latency']:.0f} ms/q")
    except Exception as e:  # noqa: BLE001 — record honestly rather than fabricate
        ce_error = f"{type(e).__name__}: {e}"
        print(f"  Cross-encoder: UNAVAILABLE — {ce_error}")

    # --- report ---
    lines = [
        f"# EXP-009: Reranker bake-off — Haiku vs cross-encoder ({date.today().isoformat()})",
        "", "Related ADR: ADR-014 (reranker & pool). Plan ref: WI-7.",
        f"Same hybrid pool of {POOL} -> top-{TOP_K}, {len(queries)} golden queries.", "",
        "## Hypothesis",
        "A dedicated cross-encoder (attends to query+passage jointly) might beat the Haiku LLM reranker "
        "on ranking quality and/or latency. Haiku is the incumbent — only switch on a measured win.", "",
        "## Results",
        "| reranker | MRR | precision@1 | recall@1/3/5 | latency ms/q |",
        "|---|---|---|---|---|",
        f"| {haiku['name']} | {haiku['mrr']:.2f} | {haiku['p1']:.2f} | "
        f"{haiku['recall'][1]:.2f}/{haiku['recall'][3]:.2f}/{haiku['recall'][5]:.2f} | {haiku['latency']:.0f} |",
    ]
    if ce:
        lines.append(
            f"| {ce['name']} | {ce['mrr']:.2f} | {ce['p1']:.2f} | "
            f"{ce['recall'][1]:.2f}/{ce['recall'][3]:.2f}/{ce['recall'][5]:.2f} | {ce['latency']:.0f} |")
    else:
        lines.append(f"| Cross-encoder ({CE_MODEL}) | — | — | — | deferred: `{ce_error}` |")
    lines += ["", "## Verdict", "TODO_VERDICT", ""]

    (REPORTS / "EXP-009-reranker-bakeoff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n  report -> docs/experiments/EXP-009-reranker-bakeoff.md (fill in the verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
