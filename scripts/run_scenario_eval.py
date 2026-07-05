"""Phase 5 scenario eval — finding precision/recall + citation faithfulness.

Runs the full pipeline (agent -> synthesis) over the gold scenarios and scores the GAP findings
against expected_gap_obligations. Includes a COMPLIANT control scenario that must yield zero findings
(guards against hallucinated gaps).

Usage:  python scripts/run_scenario_eval.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.synthesis.synthesize import analyze_scenario  # noqa: E402
from eval.harness import load_scenarios                 # noqa: E402


def main() -> int:
    scenarios = load_scenarios()
    tp = fp = fn = 0
    grounded_total = grounded_ok = 0
    compliant_ok = None

    for s in scenarios:
        res = analyze_scenario(s["scenario"])
        predicted = {f["obligation_id"] for f in res["findings"]}
        expected = set(s["expected_gap_obligations"])
        s_tp = len(predicted & expected); s_fp = len(predicted - expected); s_fn = len(expected - predicted)
        tp += s_tp; fp += s_fp; fn += s_fn

        # citation faithfulness: every finding's obligation must have been considered by the agent
        considered = {o["obligation_id"] for o in res["obligations_considered"]}
        for f in res["findings"]:
            grounded_total += 1
            grounded_ok += 1 if f["obligation_id"] in considered else 0

        if s["type"] == "compliant":
            compliant_ok = (len(predicted) == 0)

        print(f"{s['id']} [{s['type']:<13}] predicted={sorted(predicted)} expected={sorted(expected)} "
              f"TP={s_tp} FP={s_fp} FN={s_fn}")

    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    faith = grounded_ok / grounded_total if grounded_total else 1.0
    print("\n## Phase 5 scenario eval")
    print(f"  finding precision: {prec:.2f}  ({tp} TP / {tp+fp} predicted)")
    print(f"  finding recall:    {rec:.2f}  ({tp} TP / {tp+fn} expected)")
    print(f"  citation faithfulness (findings grounded in considered obligations): {faith:.2f}")
    print(f"  compliant control (S06) produced zero findings: {compliant_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
