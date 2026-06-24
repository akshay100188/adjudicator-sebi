"""Run the Phase 3 retrieval experiments and print result tables.

EXP-001  retriever comparison: dense vs sparse vs hybrid vs hybrid+rerank
EXP-002  RRF k sweep (rank-fusion constant)
EXP-003  candidate pool size sweep (dense_k = sparse_k)
EXP-004  rerank on/off (precision/MRR lift vs latency cost)

Query embeddings are computed once and cached across all configs.

Usage:  python scripts/run_retrieval_experiments.py [--no-rerank]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.tools import retrieval as R          # noqa: E402
from app.tools.rerank import rerank            # noqa: E402
from eval.harness import evaluate, load_golden, table  # noqa: E402


def main(do_rerank: bool) -> int:
    queries = load_golden()
    print(f"Golden query set: {len(queries)} queries\n")

    # Cache query embeddings once (cost discipline).
    qv = {q.id: R.embed_query(q.query) for q in queries}

    def ids(hits):
        return [h.obligation_id for h in hits]

    # ---------- EXP-001: retriever comparison ----------
    POOL, RRF, K = 10, 60, 5
    e1 = [
        evaluate("dense", lambda q: ids(R.dense_search(q.query, POOL, qv=qv[q.id]))[:K], queries),
        evaluate("sparse (BM25-ish)", lambda q: ids(R.sparse_search(q.query, POOL))[:K], queries),
        evaluate(f"hybrid RRF(k={RRF})",
                 lambda q: ids(R.hybrid_search(q.query, POOL, POOL, RRF, K, qv=qv[q.id])), queries),
    ]
    if do_rerank:
        e1.append(evaluate("hybrid + Haiku rerank",
                  lambda q: ids(rerank(q.query, R.hybrid_search(q.query, POOL, POOL, RRF, POOL, qv=qv[q.id]), K)),
                  queries))
    print("## EXP-001 — retriever comparison (pool=10, RRF k=60, metrics@1/3/5)\n")
    print(table(e1) + "\n")

    # ---------- EXP-002: RRF k sweep ----------
    e2 = [
        evaluate(f"hybrid RRF(k={rk})",
                 lambda q, rk=rk: ids(R.hybrid_search(q.query, POOL, POOL, rk, K, qv=qv[q.id])), queries)
        for rk in (10, 30, 60, 100)
    ]
    print("## EXP-002 — RRF k sweep (pool=10, metrics@1/3/5)\n")
    print(table(e2) + "\n")

    # ---------- EXP-003: candidate pool size sweep ----------
    e3 = [
        evaluate(f"hybrid pool={p}",
                 lambda q, p=p: ids(R.hybrid_search(q.query, p, p, RRF, K, qv=qv[q.id])), queries)
        for p in (3, 5, 8, 16)
    ]
    print("## EXP-003 — candidate pool size sweep (RRF k=60, metrics@1/3/5)\n")
    print(table(e3) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(do_rerank="--no-rerank" not in sys.argv))
