"""WI-1 — Post-rerank recall eval (ADR-019, second tier of the two-tier recall protection).

The deterministic regression gate (ADR-015, eval/regression_gate.py) measures *pool* recall on
raw hybrid retrieval — no rerank. That is the right CI tripwire: fast, free, deterministic. But the
agent does NOT consume the raw pool; it consumes the **reranked top-5 out of a pool of 10** (ADR-014).
The reranker can reorder a gold obligation out of the top-5, and the gate never runs it — so a
reranker regression that silently drops a real obligation would not trip CI.

This eval measures the recall the agent actually *experiences*: it runs the SAME hybrid_search +
rerank tools the agent calls (imported, not reimplemented), computes post-rerank recall@{1,3,5},
emits a delta vs the raw-hybrid pool recall, and logs every "rerank drop" — a query where the gold
obligation was present in the raw pool but absent from the reranked top-k. Those drops are exactly
what the deterministic gate cannot see.

NOT part of CI: it is LLM-based (Haiku), nondeterministic, and costs money. Run on demand / nightly /
pre-release. The deterministic gate stays exactly as-is.

Usage:  python eval/rerank_recall_eval.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.tools import retrieval as R          # noqa: E402
from app.tools.rerank import rerank           # noqa: E402
from eval.harness import load_golden, recall_at_k  # noqa: E402

# Match the pipeline the agent runs (ADR-014): hybrid pool of 10, RRF k=60, rerank to top-5.
POOL, RRF, TOP_K = 10, 60, 5
KS = (1, 3, 5)
REPORTS = ROOT / "eval" / "reports"


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def main() -> int:
    queries = load_golden()
    qv = {q.id: R.embed_query(q.query) for q in queries}  # embed once, reuse (cost discipline)

    pool_recall: dict[int, list[float]] = {k: [] for k in KS}
    rerank_recall: dict[int, list[float]] = {k: [] for k in KS}
    drops: list[dict] = []  # gold in raw pool but out of reranked top_k

    print(f"Post-rerank recall eval — {len(queries)} golden queries, "
          f"pool={POOL} RRF={RRF} rerank->top{TOP_K}\n")

    for q in queries:
        pool_hits = R.hybrid_search(q.query, POOL, POOL, RRF, POOL, qv=qv[q.id])
        pool_ids = [h.obligation_id for h in pool_hits]
        reranked_ids = [h.obligation_id for h in rerank(q.query, pool_hits, top_k=TOP_K)]

        for k in KS:
            pool_recall[k].append(recall_at_k(q.expected, pool_ids, k))
            rerank_recall[k].append(recall_at_k(q.expected, reranked_ids, k))

        # rerank drop: a gold obligation the raw pool retrieved that the reranker pushed out of top_k
        pool_set, top_set = set(pool_ids[:POOL]), set(reranked_ids[:TOP_K])
        lost = sorted((q.expected & pool_set) - top_set)
        if lost:
            drops.append({"id": q.id, "query": q.query, "lost": lost,
                          "pool_rank": {o: pool_ids.index(o) + 1 for o in lost}})
        mark = "  DROP" if lost else ""
        print(f"  {q.id}: pool_r@5={recall_at_k(q.expected, pool_ids, 5):.2f} "
              f"rerank_r@5={recall_at_k(q.expected, reranked_ids, 5):.2f}{mark}")

    # --- delta table -------------------------------------------------------
    lines = [
        f"# Post-rerank recall eval — {date.today().isoformat()}",
        "",
        f"Config: hybrid pool={POOL}, RRF k={RRF}, Haiku rerank -> top-{TOP_K}. "
        f"{len(queries)} golden queries. Same tools the agent calls (ADR-014).",
        "",
        "Guards the recall the agent **actually consumes** (reranked top-5), which the deterministic "
        "CI gate (raw pool recall) never measures. See ADR-019.",
        "",
        "## Recall: raw hybrid pool vs. reranked top-k",
        "",
        "| metric | raw-hybrid pool | post-rerank | delta |",
        "|---|---|---|---|",
    ]
    for k in KS:
        p, r = _mean(pool_recall[k]), _mean(rerank_recall[k])
        lines.append(f"| recall@{k} | {p:.2f} | {r:.2f} | {r - p:+.2f} |")

    lines += ["", "## Rerank drops (gold in raw pool, absent from reranked top-{})".format(TOP_K), ""]
    if drops:
        lines += ["These are exactly the failures the deterministic CI gate cannot see.", "",
                  "| query id | lost obligation(s) | rank in raw pool |", "|---|---|---|"]
        for d in drops:
            ranks = ", ".join(f"{o}@{d['pool_rank'][o]}" for o in d["lost"])
            lines.append(f"| {d['id']} | {', '.join(d['lost'])} | {ranks} |")
    else:
        lines.append("**None.** The reranker did not drop a single gold obligation that the raw pool "
                     "retrieved — it is faithful: it reorders for precision without costing recall.")
    lines.append("")

    REPORTS.mkdir(parents=True, exist_ok=True)
    report = REPORTS / f"rerank_recall_{date.today().isoformat()}.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n## Recall delta (raw pool -> post-rerank)")
    for k in KS:
        p, r = _mean(pool_recall[k]), _mean(rerank_recall[k])
        print(f"  recall@{k}: pool {p:.2f} -> rerank {r:.2f}  ({r - p:+.2f})")
    print(f"\n  rerank drops: {len(drops)}")
    print(f"  report written -> {report.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
