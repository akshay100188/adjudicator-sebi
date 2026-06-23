"""Phase 1 metric gate.

Seeds the synthetic structural fixture (idempotent), then proves against the
live DB:
  1. Temporal validity (adj_valid_obligations) returns the right set at 3 dates.
  2. Recursive citation-graph traversal (adj_relation_closure) walks the chain.
  3. Corpus-health: % obligations with resolved temporal metadata == 100%.

Exit code 0 only if every assertion + the gate threshold pass.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.db import get_cursor  # noqa: E402

FIXTURE = ROOT / "data" / "obligations" / "_fixture_synthetic.json"


def seed(cur, data: dict) -> None:
    for s in data["sections"]:
        cur.execute(
            """insert into adj_obligation_section (section_id, circular_ref, heading, full_text)
               values (%(section_id)s, %(circular_ref)s, %(heading)s, %(full_text)s)
               on conflict (section_id) do update set
                 circular_ref = excluded.circular_ref,
                 heading = excluded.heading,
                 full_text = excluded.full_text;""",
            s,
        )
    # Pass 1: insert obligations with superseded_by NULL (avoids FK ordering issues).
    for o in data["obligations"]:
        row = {**o, "superseded_by": None}
        cur.execute(
            """insert into adj_obligation
                 (obligation_id, obligation_text, source_circular_ref, source_url,
                  issue_date, effective_date, superseded_by, regulation_family,
                  intermediary_type, category, parent_section_id, is_synthetic)
               values
                 (%(obligation_id)s, %(obligation_text)s, %(source_circular_ref)s, %(source_url)s,
                  %(issue_date)s, %(effective_date)s, NULL, 'stock_brokers',
                  %(intermediary_type)s, %(category)s, %(parent_section_id)s, %(is_synthetic)s)
               on conflict (obligation_id) do update set
                 obligation_text = excluded.obligation_text,
                 effective_date  = excluded.effective_date,
                 issue_date      = excluded.issue_date,
                 superseded_by   = NULL;""",
            row,
        )
    # Pass 2: set superseded_by now that all rows exist.
    for o in data["obligations"]:
        if o.get("superseded_by"):
            cur.execute(
                "update adj_obligation set superseded_by = %s where obligation_id = %s;",
                (o["superseded_by"], o["obligation_id"]),
            )
    for r in data["relations"]:
        cur.execute(
            """insert into adj_obligation_relations (from_ref, to_ref, relation_type, source_note)
               values (%(from_ref)s, %(to_ref)s, %(relation_type)s, %(source_note)s)
               on conflict (from_ref, to_ref, relation_type) do nothing;""",
            r,
        )


def valid_ids(cur, as_of: date) -> set[str]:
    cur.execute(
        "select obligation_id from adj_valid_obligations(%s, 'stock_brokers') "
        "where obligation_id like 'ADJ-SYN-%%' order by 1;",
        (as_of,),
    )
    return {r["obligation_id"] for r in cur.fetchall()}


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []

    with get_cursor(commit=True) as cur:
        seed(cur, data)

    with get_cursor() as cur:
        # --- 1. Temporal validity at three points in time ---
        cases = {
            date(2019, 1, 1): {"ADJ-SYN-001"},  # only base effective; superseder (2021) not yet
            date(2022, 1, 1): {"ADJ-SYN-002"},  # base superseded; master (2024) not yet
            date(2024, 6, 1): {"ADJ-SYN-003"},  # master circular now valid
        }
        for as_of, expected in cases.items():
            got = valid_ids(cur, as_of)
            ok = got == expected
            print(f"[temporal] as_of {as_of}: valid={sorted(got)} expected={sorted(expected)} -> {'PASS' if ok else 'FAIL'}")
            if not ok:
                failures.append(f"temporal {as_of}: got {got}, expected {expected}")

        # --- 2. Recursive citation-graph traversal ---
        cur.execute(
            "select to_ref, relation_type, depth from adj_relation_closure('ADJ-SYN-003') order by depth, to_ref;"
        )
        rows = cur.fetchall()
        reached = {r["to_ref"] for r in rows}
        expected_reach = {"ADJ-SYN-002", "ADJ-SYN-001"}
        ok = expected_reach.issubset(reached)
        print(f"[graph] closure(ADJ-SYN-003) reached={sorted(reached)} depth_max={max((r['depth'] for r in rows), default=0)} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append(f"graph closure: reached {reached}, expected superset of {expected_reach}")

        # --- 3. Corpus-health metric gate: temporal metadata resolution ---
        cur.execute(
            """select count(*) as total,
                      count(*) filter (where effective_date is not null and issue_date is not null) as resolved
               from adj_obligation where is_synthetic = true;"""
        )
        h = cur.fetchone()
        pct = (h["resolved"] / h["total"] * 100) if h["total"] else 0
        gate_ok = pct == 100.0
        print(f"[corpus-health] temporal metadata resolved: {h['resolved']}/{h['total']} = {pct:.0f}% (gate: 100%) -> {'PASS' if gate_ok else 'FAIL'}")
        if not gate_ok:
            failures.append(f"corpus-health: {pct:.0f}% < 100%")

    print("\n" + ("PHASE 1 GATE: PASS" if not failures else "PHASE 1 GATE: FAIL\n - " + "\n - ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
