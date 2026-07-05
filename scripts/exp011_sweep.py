"""EXP-011 corrective-retrieval sweep — resumable, cache-backed (WI-2 baseline + WI-4 sweep).

Agent runs are slow (~40s each; multi-hop reformulations slower) and the shell caps jobs at ~10 min,
so a full 3-reps x 11-queries x 3-levels sweep can't finish in one process. This script persists every
completed (strictness, query_id, rep) -> correction_fired result to a JSONL cache and SKIPS ones already
done, so you can invoke it repeatedly until complete and it resumes. Each invocation also prints the
current sensitivity/specificity for the requested strictness from everything cached so far.

Usage:  python scripts/exp011_sweep.py <strictness> <reps>     # e.g. 1 3
        python scripts/exp011_sweep.py report                  # aggregate all levels, no runs
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "backend"))

from app.agent.agent import run_agent            # noqa: E402
from eval.harness import load_trajectories       # noqa: E402

CACHE = ROOT / "docs" / "experiments" / "_correction_runs.jsonl"


def load_cache() -> list[dict]:
    if not CACHE.exists():
        return []
    return [json.loads(l) for l in CACHE.read_text(encoding="utf-8").splitlines() if l.strip()]


def aggregate(cache: list[dict]) -> None:
    gold = {g["id"]: bool(g.get("correction_expected")) for g in load_trajectories()}
    pos = sorted(i for i, e in gold.items() if e)
    neg = sorted(i for i, e in gold.items() if not e)
    by_lvl = defaultdict(lambda: defaultdict(list))  # strictness -> id -> [fired,...]
    for r in cache:
        by_lvl[r["strictness"]][r["id"]].append(int(r["fired"]))
    print("\n## EXP-011 sweep — sensitivity vs specificity (from cache)")
    print(f"  correction-EXPECTING (n={len(pos)}): {pos}")
    print(f"  NOT-expecting        (n={len(neg)}): {neg}\n")
    print("| strictness | sensitivity (fire|should) | specificity (¬fire|shouldn't) | reps/query |")
    print("|---|---|---|---|")
    for lvl in sorted(by_lvl):
        d = by_lvl[lvl]
        pos_fires = sum(sum(d.get(i, [])) for i in pos)
        pos_runs = sum(len(d.get(i, [])) for i in pos)
        neg_fires = sum(sum(d.get(i, [])) for i in neg)
        neg_runs = sum(len(d.get(i, [])) for i in neg)
        sens = pos_fires / pos_runs if pos_runs else float("nan")
        spec = (neg_runs - neg_fires) / neg_runs if neg_runs else float("nan")
        reps = f"{min((len(d.get(i,[])) for i in pos+neg), default=0)}-{max((len(d.get(i,[])) for i in pos+neg), default=0)}"
        print(f"| {lvl} | {sens:.2f} ({pos_fires}/{pos_runs}) | {spec:.2f} ({neg_runs-neg_fires}/{neg_runs}) | {reps} |")
    # per-query fire rates per level
    print("\n### per-query fire rate (fired/runs) by strictness")
    ids = pos + neg
    print("| id | class | " + " | ".join(f"L{l}" for l in sorted(by_lvl)) + " |")
    print("|---|---|" + "|".join("---" for _ in by_lvl) + "|")
    for i in ids:
        cls = "EXPECT" if gold[i] else "clean"
        cells = []
        for lvl in sorted(by_lvl):
            fs = by_lvl[lvl].get(i, [])
            cells.append(f"{sum(fs)}/{len(fs)}" if fs else "-")
        print(f"| {i} | {cls} | " + " | ".join(cells) + " |")


def main() -> int:
    if sys.argv[1:] and sys.argv[1] == "report":
        aggregate(load_cache())
        return 0
    strictness = int(sys.argv[1]) if sys.argv[1:] else 0
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    gold = load_trajectories()
    done = {(r["strictness"], r["id"], r["rep"]) for r in load_cache()}
    todo = [(g, rep) for g in gold for rep in range(reps) if (strictness, g["id"], rep) not in done]
    print(f"strictness={strictness} reps={reps}: {len(todo)} runs to do "
          f"({len(gold)*reps - len(todo)} already cached)")

    with CACHE.open("a", encoding="utf-8") as f:
        for g, rep in todo:
            res = run_agent(g["query"], correction_strictness=strictness)
            rec = {"strictness": strictness, "id": g["id"], "rep": rep,
                   "fired": bool(res.correction_fired), "gold": bool(g.get("correction_expected"))}
            f.write(json.dumps(rec) + "\n"); f.flush()
            print(f"  {g['id']} rep{rep} L{strictness}: fired={rec['fired']} gold={rec['gold']} "
                  f"{'ok' if rec['fired']==rec['gold'] else 'MISS'}", flush=True)

    aggregate(load_cache())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
