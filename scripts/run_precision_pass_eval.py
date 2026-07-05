"""EXP-006 — synthesis precision pass (ADR-017 §3, WI-A).

Measures the second-pass adjudication's effect on finding precision, with recall held at 1.00. For each
gold scenario it runs the agent + first synthesis ONCE (the expensive part), then compares:
  - BEFORE: raw synthesis findings (recall-first, over-flags)
  - AFTER:  findings surviving the adjudication pass (drops merely-topical false positives)
so both arms share the same retrieval + first-pass output (cheap, apples-to-apples).

Hard constraint: recall must stay 1.00 and the S06 compliant control must stay at 0 findings. Precision
gains that cost recall are rejected — if that happens, the correct outcome is to document the trade.

Usage:  python scripts/run_precision_pass_eval.py
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.agent.agent import run_agent                              # noqa: E402
from app.synthesis.synthesize import synthesize, adjudicate, _fetch  # noqa: E402
from eval.harness import load_scenarios                            # noqa: E402

REPORTS = ROOT / "docs" / "experiments"


def prf(tp, fp, fn):
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    return prec, rec


def main() -> int:
    scenarios = load_scenarios()
    b = {"tp": 0, "fp": 0, "fn": 0, "gt": 0, "gok": 0}  # before
    a = {"tp": 0, "fp": 0, "fn": 0, "gt": 0, "gok": 0}  # after
    compliant_before = compliant_after = None
    drop_log: list[dict] = []

    for s in scenarios:
        agent = run_agent(s["scenario"])
        obligations = _fetch(agent.relevant_obligations)
        considered = set(obligations)
        raw = synthesize(s["scenario"], obligations)
        kept, rejected = adjudicate(s["scenario"], raw, obligations)

        expected = set(s["expected_gap_obligations"])
        before_ids = {f.obligation_id for f in raw}
        after_ids = {f.obligation_id for f in kept}

        for tag, pred, acc in (("b", before_ids, b), ("a", after_ids, a)):
            acc["tp"] += len(pred & expected); acc["fp"] += len(pred - expected); acc["fn"] += len(expected - pred)
            for oid in pred:
                acc["gt"] += 1; acc["gok"] += 1 if oid in considered else 0

        if s["type"] == "compliant":
            compliant_before = len(before_ids) == 0
            compliant_after = len(after_ids) == 0

        for r in rejected:
            correct = r["obligation_id"] not in expected  # a good drop = it wasn't an expected gap
            drop_log.append({"id": s["id"], **r, "correct_drop": correct})

        print(f"{s['id']} [{s['type']:<13}] before={sorted(before_ids)} -> after={sorted(after_ids)} "
              f"expected={sorted(expected)} dropped={[r['obligation_id'] for r in rejected]}")

    pb, rb = prf(b["tp"], b["fp"], b["fn"])
    pa, ra = prf(a["tp"], a["fp"], a["fn"])
    fb = b["gok"] / b["gt"] if b["gt"] else 1.0
    fa = a["gok"] / a["gt"] if a["gt"] else 1.0
    good_drops = sum(1 for d in drop_log if d["correct_drop"])

    print("\n## EXP-006 precision pass — before vs after")
    print(f"  precision:  {pb:.2f} -> {pa:.2f}")
    print(f"  recall:     {rb:.2f} -> {ra:.2f}   (must stay 1.00)")
    print(f"  faithfulness:{fb:.2f} -> {fa:.2f}")
    print(f"  S06 compliant control = 0 findings:  before={compliant_before} after={compliant_after}")
    print(f"  drops: {len(drop_log)} total, {good_drops} correct (removed a non-expected obligation)")

    lines = [
        f"# EXP-006: Synthesis precision pass — second-pass adjudication ({date.today().isoformat()})",
        "", "Related ADR: ADR-017 (grounded synthesis). Plan ref: WI-A.",
        f"Full pipeline (agent -> synthesis) over {len(scenarios)} gold scenarios "
        "(5 non-compliant + 1 compliant control). Shared agent + first-pass; before = raw findings, "
        "after = adjudicated.", "",
        "## Hypothesis",
        "A strict per-finding second pass drops 'merely topically related' false positives (the EXP-005 "
        "residual at precision 0.76) while holding recall at 1.00.", "",
        "## Metric before / after",
        "| metric | before (raw) | after (adjudicated) |",
        "|---|---|---|",
        f"| finding precision | {pb:.2f} | {pa:.2f} |",
        f"| finding recall | {rb:.2f} | {ra:.2f} |",
        f"| citation faithfulness | {fb:.2f} | {fa:.2f} |",
        f"| S06 compliant control -> 0 findings | {'PASS' if compliant_before else 'FAIL'} "
        f"| {'PASS' if compliant_after else 'FAIL'} |",
        "", "## Rejected findings (auditable drop log)",
        "| scenario | dropped obligation | correct drop? | reason |", "|---|---|---|---|",
    ]
    for d in drop_log:
        lines.append(f"| {d['id']} | {d['obligation_id']} | {'yes' if d['correct_drop'] else 'NO (true gap!)'} "
                     f"| {d['reason']} |")
    if not drop_log:
        lines.append("| — | — | — | (nothing dropped) |")
    lines += ["", "## Verdict", "TODO_VERDICT", ""]

    (REPORTS / "EXP-006-precision-pass.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n  report -> docs/experiments/EXP-006-precision-pass.md (fill in the verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
