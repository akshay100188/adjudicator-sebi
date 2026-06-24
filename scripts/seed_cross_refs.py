"""Seed curated obligation-level `refers_to` cross-edges into the citation graph.

Unlike the circular-level edges (consolidated_by/supersedes/amends, auto-extracted from footnotes),
these are obligation->obligation references grounded in SHARED DEFINED TERMS across chapters — e.g. a
running-account clause that says funds stay "in the USCNBA", where USCNBA is defined in the upstreaming
chapter. Each edge is hand-verified to the text (the rationale is in source_note). Idempotent.

Usage:  python scripts/seed_cross_refs.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.db import get_cursor  # noqa: E402

# (from_obligation, to_obligation, shared term / rationale)
CROSS_REFS = [
    ("SB-RUNACCT-003", "SB-UPSTREAM-002", "ring-fences funds in the USCNBA, defined here"),
    ("SB-UPSTREAM-013", "SB-UPSTREAM-002", "retains balances in the USCNBA, defined here"),
    ("SB-CLTSEC-007", "SB-CLTSEC-002", "trail in the 'client unpaid securities pledgee account', defined here"),
    ("SB-CLTSEC-010", "SB-CLTSEC-002", "refers to securities in the pledgee account, defined here"),
    ("SB-CLTSEC-011", "SB-CLTSEC-002", "restricts the pledgee account, defined here"),
    ("SB-UPSTREAM-009", "SB-UPSTREAM-008", "MFOS account for the MFOS investment defined here"),
    ("SB-UPSTREAM-010", "SB-UPSTREAM-008", "pledges the MFOS units defined here"),
]


def main() -> int:
    with get_cursor(commit=True) as cur:
        cur.execute("select obligation_id from adj_obligation where is_synthetic=false;")
        valid = {r["obligation_id"] for r in cur.fetchall()}
        n = 0
        for frm, to, note in CROSS_REFS:
            if frm not in valid or to not in valid:
                print(f"  skip {frm}->{to} (missing obligation)")
                continue
            cur.execute(
                """insert into adj_obligation_relations (from_ref, to_ref, relation_type, source_note)
                   values (%s, %s, 'refers_to', %s)
                   on conflict (from_ref, to_ref, relation_type) do update set source_note=excluded.source_note;""",
                (frm, to, f"cross-reference: {note}"),
            )
            n += 1
        cur.execute("select count(*) c from adj_obligation_relations where relation_type='refers_to';")
        print(f"Seeded {n} refers_to cross-edges. Total refers_to edges: {cur.fetchone()['c']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
