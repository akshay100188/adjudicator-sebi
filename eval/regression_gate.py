"""Phase 6 regression gate — guards recall so tuning can't silently degrade it.

Runs the deterministic recall-first retrieval (hybrid candidate generation, NO rerank — so the
gate is free of LLM cost/nondeterminism) over the golden query set and asserts thresholds. The
reranker improves *ranking*, not pool recall, so recall is the right thing to gate here.

Exit code 0 only if all thresholds pass. Wire into CI / run before/after any retrieval change.

Usage:  python eval/regression_gate.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.tools import retrieval as R       # noqa: E402
from eval.harness import evaluate, load_golden, table  # noqa: E402

# Thresholds — set just below measured hybrid (EXP-004: recall@5 0.99, recall@3 0.84).
THRESHOLDS = {
    ("recall", 5): 0.95,
    ("recall", 3): 0.80,
    ("recall", 1): 0.45,
}
POOL, RRF, K = 10, 60, 5


def main() -> int:
    queries = load_golden()
    qv = {q.id: R.embed_query(q.query) for q in queries}
    res = evaluate(
        "hybrid (gate)",
        lambda q: [h.obligation_id for h in R.hybrid_search(q.query, POOL, POOL, RRF, K, qv=qv[q.id])],
        queries,
    )
    print(f"Regression gate — {len(queries)} golden queries, config: hybrid pool={POOL} RRF={RRF}\n")
    print(table([res]) + "\n")

    failures = []
    for (metric, k), thr in THRESHOLDS.items():
        got = getattr(res, metric)[k]
        ok = got >= thr
        print(f"  {metric}@{k}: {got:.2f}  (>= {thr})  {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"{metric}@{k} {got:.2f} < {thr}")

    print("\n" + ("REGRESSION GATE: PASS" if not failures else "REGRESSION GATE: FAIL\n - " + "\n - ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
