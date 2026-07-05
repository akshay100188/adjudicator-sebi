"""Probe: is the agent's corrective re-retrieval (CRAG) 3/4 a variance blip or a real gap?

Runs each gold trajectory query REPS times and tallies how often correction_fired matches the gold
expectation — isolating the one nondeterministic agent metric. T03 is the query that SHOULD trigger
correction (lay phrasing 'client money' -> canonical reformulation); the others should not.

Usage:  python scripts/probe_correction_variance.py [reps]
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "backend"))

from app.agent.agent import run_agent            # noqa: E402
from eval.harness import load_trajectories       # noqa: E402

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 4
STRICTNESS = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # correction-clause level (EXP-011 sweep)


def main() -> int:
    gold = load_trajectories()
    fired = defaultdict(int)
    match = defaultdict(int)
    print(f"Correction-trigger variance probe — {REPS} reps/query, strictness={STRICTNESS}\n")
    for g in gold:
        exp = bool(g.get("correction_expected"))
        for r in range(REPS):
            res = run_agent(g["query"], correction_strictness=STRICTNESS)
            f = bool(res.correction_fired)
            fired[g["id"]] += int(f)
            match[g["id"]] += int(f == exp)
            print(f"  {g['id']} rep{r+1}: correction_fired={f}  (gold={exp})  {'ok' if f == exp else 'MISS'}")
    print("\n## Summary (correction_fired count / matches-gold count, out of", REPS, "reps)")
    for g in gold:
        exp = bool(g.get("correction_expected"))
        print(f"  {g['id']} (gold correction={exp}): fired {fired[g['id']]}/{REPS}, "
              f"matched gold {match[g['id']]}/{REPS}")

    # Sensitivity = P(fire | should fire); Specificity = P(not fire | should not fire) — averaged over reps.
    pos = [g for g in gold if bool(g.get("correction_expected"))]
    neg = [g for g in gold if not bool(g.get("correction_expected"))]
    sens = sum(fired[g["id"]] for g in pos) / (len(pos) * REPS) if pos else 0.0
    spec = sum(REPS - fired[g["id"]] for g in neg) / (len(neg) * REPS) if neg else 0.0
    print(f"\n  SENSITIVITY (correction-expecting fired): {sens:.2f}  "
          f"(over {len(pos)} queries x {REPS} reps)")
    print(f"  SPECIFICITY (not-expecting did NOT fire): {spec:.2f}  "
          f"(over {len(neg)} queries x {REPS} reps)")
    total = sum(match.values()); denom = len(gold) * REPS
    print(f"  correction-trigger accuracy across all runs: {total}/{denom} = {total/denom:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
