"""Retrieval eval harness: metrics + a config runner over the golden query set.

Metrics are recall-first (the worst failure in compliance is a missed obligation).
Query embeddings are computed once and reused across configs (cost discipline).
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "eval" / "golden" / "queries.jsonl"


@dataclass
class Query:
    id: str
    query: str
    expected: set[str]
    type: str


def load_golden() -> list[Query]:
    out = []
    for line in GOLDEN.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out.append(Query(d["id"], d["query"], set(d["expected"]), d.get("type", "")))
    return out


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_scenarios() -> list[dict]:
    """Gold scenarios: scenario text + declared controls -> expected gap obligation IDs (Phase 5)."""
    return _load_jsonl(ROOT / "eval" / "golden" / "scenarios.jsonl")


def load_trajectories() -> list[dict]:
    """Gold trajectories: query -> expected tool sequence (Phase 4 agent eval, §7)."""
    return _load_jsonl(ROOT / "eval" / "golden" / "trajectories.jsonl")


# --- trajectory / process metrics (§7) — used by the Phase 4 agent eval ------
def tool_set_overlap(gold: list[str], actual: list[str]) -> float:
    """Order-agnostic Jaccard of tool sets."""
    g, a = set(gold), set(actual)
    return len(g & a) / len(g | a) if (g | a) else 1.0


def trajectory_order_match(gold: list[str], actual: list[str]) -> bool:
    """Exact tool sequence match after collapsing consecutive duplicates."""
    def collapse(xs):
        out = []
        for x in xs:
            if not out or out[-1] != x:
                out.append(x)
        return out
    return collapse(gold) == collapse(actual)


def key_tool_hit(key_tool: str, actual: list[str]) -> bool:
    return key_tool in actual


# --- metrics (binary relevance) ----------------------------------------------
def recall_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(relevant & set(ranked[:k])) / len(relevant)


def precision_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    return len(relevant & set(ranked[:k])) / k


def reciprocal_rank(relevant: set[str], ranked: list[str]) -> float:
    for i, oid in enumerate(ranked, start=1):
        if oid in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(relevant: set[str], ranked: list[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(i + 1) for i, oid in enumerate(ranked[:k], start=1) if oid in relevant)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    return dcg / idcg if idcg else 0.0


@dataclass
class Result:
    name: str
    ks: list[int]
    recall: dict[int, float]
    precision: dict[int, float]
    mrr: float
    ndcg: dict[int, float]
    avg_latency_ms: float
    extra: dict = field(default_factory=dict)

    def row(self) -> str:
        r = " / ".join(f"{self.recall[k]:.2f}" for k in self.ks)
        p = " / ".join(f"{self.precision[k]:.2f}" for k in self.ks)
        n = " / ".join(f"{self.ndcg[k]:.2f}" for k in self.ks)
        return f"| {self.name} | {r} | {p} | {self.mrr:.2f} | {n} | {self.avg_latency_ms:.0f} |"


def evaluate(name: str, retrieve: Callable[[Query], list[str]], queries: list[Query],
             ks: tuple[int, ...] = (1, 3, 5)) -> Result:
    rankings, latencies = [], []
    for q in queries:
        t0 = time.perf_counter()
        ranked = retrieve(q)
        latencies.append((time.perf_counter() - t0) * 1000)
        rankings.append((q.expected, ranked))
    rec = {k: sum(recall_at_k(r, rk, k) for r, rk in rankings) / len(rankings) for k in ks}
    prec = {k: sum(precision_at_k(r, rk, k) for r, rk in rankings) / len(rankings) for k in ks}
    nd = {k: sum(ndcg_at_k(r, rk, k) for r, rk in rankings) / len(rankings) for k in ks}
    mrr = sum(reciprocal_rank(r, rk) for r, rk in rankings) / len(rankings)
    return Result(name, list(ks), rec, prec, mrr, nd, sum(latencies) / len(latencies))


def table(results: list[Result], ks=(1, 3, 5)) -> str:
    head = (
        f"| config | recall@{'/'.join(map(str, ks))} | precision@{'/'.join(map(str, ks))} "
        f"| MRR | nDCG@{'/'.join(map(str, ks))} | latency ms |\n"
        f"|---|---|---|---|---|---|"
    )
    return head + "\n" + "\n".join(r.row() for r in results)
