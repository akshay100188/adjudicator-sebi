"""Phase 4 agent (trajectory) evaluation — §7 process metrics.

Runs the agent over the gold trajectory set and scores BOTH outcome and path:
  - route_match            did it pick simple vs multi-hop correctly?
  - key_tool_hit           did it call the decisive tool (e.g. graph_lookup on supersession)?
  - tool_set_overlap       Jaccard of tool sets vs the gold trajectory
  - correction_match       did corrective re-retrieval fire when expected (and not otherwise)?
  - grounding_clean        zero hallucinated obligation IDs (Self-RAG gate)
Writes a TRAJ-*.md per query (the trajectory viewer's data + showcase artifact).

Usage:  python scripts/run_agent_eval.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.agent.agent import run_agent          # noqa: E402
from eval.harness import (load_trajectories, tool_set_overlap,  # noqa: E402
                          trajectory_order_match, key_tool_hit)

TRAJ_DIR = ROOT / "docs" / "trajectories"


def write_traj_md(gold: dict, res) -> None:
    lines = [
        f"# TRAJ-{gold['id']}: {gold['query']}", "",
        f"Route chosen: **{res.route}**  (gold: {gold['route']})  ",
        f"Correction fired: {res.correction_fired}  (gold expects: {gold.get('correction_expected')})  ",
        f"Steps: {res.steps_used}  ·  Grounding dropped: {res.grounding_dropped or 'none'}", "",
        "## Steps", "| # | tool | args | observation |", "|---|---|---|---|",
    ]
    for i, s in enumerate(res.trajectory, 1):
        import json as _j
        args = _j.dumps(s.args)[:60]
        obs = str(s.observation)[:80].replace("|", "\\|")
        lines.append(f"| {i} | {s.tool} | `{args}` | {obs} |")
    lines += [
        "", f"Gold tools: `{gold['expected_tools']}`  ", f"Actual tools: `{res.tool_sequence()}`  ",
        f"Key tool ({gold['key_tool']}) hit: {key_tool_hit(gold['key_tool'], res.tool_sequence())}", "",
        f"## Obligations returned\n{res.relevant_obligations}", "",
        f"## Reasoning\n{res.reasoning}", "", f"> {res.disclaimer}",
    ]
    TRAJ_DIR.mkdir(parents=True, exist_ok=True)
    (TRAJ_DIR / f"TRAJ-{gold['id']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    gold = load_trajectories()
    rows = []
    for g in gold:
        res = run_agent(g["query"])
        actual = res.tool_sequence()
        rows.append({
            "id": g["id"], "route_match": res.route == g["route"],
            "key_tool": key_tool_hit(g["key_tool"], actual),
            "overlap": tool_set_overlap(g["expected_tools"], actual),
            "correction_match": res.correction_fired == bool(g.get("correction_expected")),
            "grounding_clean": not res.grounding_dropped, "steps": res.steps_used,
        })
        write_traj_md(g, res)
        print(f"{g['id']}: route={'ok' if rows[-1]['route_match'] else 'X'} "
              f"key_tool={'ok' if rows[-1]['key_tool'] else 'X'} "
              f"overlap={rows[-1]['overlap']:.2f} "
              f"correction={'ok' if rows[-1]['correction_match'] else 'X'} "
              f"grounded={'ok' if rows[-1]['grounding_clean'] else 'X'} steps={res.steps_used}")

    n = len(rows)
    print("\n## Agent eval summary (§7 process metrics)")
    print(f"  route accuracy:        {sum(r['route_match'] for r in rows)}/{n}")
    print(f"  key-tool accuracy:     {sum(r['key_tool'] for r in rows)}/{n}")
    print(f"  correction correctness:{sum(r['correction_match'] for r in rows)}/{n}")
    print(f"  grounding clean:       {sum(r['grounding_clean'] for r in rows)}/{n}")
    print(f"  avg tool-set overlap:  {sum(r['overlap'] for r in rows)/n:.2f}")
    print(f"  avg steps:             {sum(r['steps'] for r in rows)/n:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
