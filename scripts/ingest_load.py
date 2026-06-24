"""Phase 2 load stage: persist reviewed chapter bundles into adj_ tables + embed chunks.

Loads ONLY obligations flagged `_approved: true` (the human-review gate, ADR-009),
unless --include-unapproved is passed. Idempotent (upserts).

Usage:
  python scripts/ingest_load.py                       # all chapter bundles, approved only
  python scripts/ingest_load.py 45 46                 # only these chapters
  python scripts/ingest_load.py 45 --include-unapproved
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.db import get_cursor                          # noqa: E402
from app.ingest.embed import embed_texts, to_pgvector  # noqa: E402

REVIEW_DIR = ROOT / "data" / "obligations" / "review"


def load_bundle(path: Path, include_unapproved: bool) -> tuple[int, int, int]:
    b = json.loads(path.read_text(encoding="utf-8"))
    master, sec = b["master"], b["parent_section"]
    obligations = [o for o in b["obligations"] if include_unapproved or o.get("_approved")]
    if not obligations:
        print(f"  {path.name}: no approved obligations, skipping")
        return 0, 0, 0

    with get_cursor(commit=True) as cur:
        cur.execute(
            """insert into adj_obligation_section (section_id, circular_ref, heading, full_text)
               values (%(section_id)s, %(circular_ref)s, %(heading)s, %(full_text)s)
               on conflict (section_id) do update set heading=excluded.heading, full_text=excluded.full_text;""",
            sec,
        )
        for o in obligations:
            cur.execute(
                """insert into adj_obligation
                     (obligation_id, obligation_text, source_circular_ref, source_url, issue_date,
                      effective_date, superseded_by, regulation_family, intermediary_type, category,
                      parent_section_id, is_synthetic, title, clause_refs, expected_controls)
                   values (%(oid)s,%(text)s,%(cref)s,%(url)s,%(idate)s,%(idate)s,NULL,'stock_brokers',
                      %(itype)s,%(cat)s,%(sec)s,false,%(title)s,%(clauses)s,%(controls)s)
                   on conflict (obligation_id) do update set
                     obligation_text=excluded.obligation_text, title=excluded.title,
                     clause_refs=excluded.clause_refs, expected_controls=excluded.expected_controls,
                     category=excluded.category, intermediary_type=excluded.intermediary_type;""",
                {"oid": o["suggested_id"], "text": o["obligation_text"], "cref": master["circular_ref"],
                 "url": master["source_url"], "idate": master["issue_date"],
                 "itype": o.get("intermediary_type"), "cat": o.get("category"), "sec": sec["section_id"],
                 "title": o.get("title"), "clauses": o.get("clause_refs"),
                 "controls": json.dumps(o.get("expected_controls", []))},
            )
        for e in b["relations"]:
            cur.execute(
                """insert into adj_obligation_relations (from_ref, to_ref, relation_type, source_note)
                   values (%(from_ref)s,%(to_ref)s,%(relation_type)s,%(source_note)s)
                   on conflict (from_ref, to_ref, relation_type) do nothing;""", e,
            )

    vectors = embed_texts([o["obligation_text"] for o in obligations])
    with get_cursor(commit=True) as cur:
        for o, vec in zip(obligations, vectors):
            cur.execute(
                """insert into adj_obligation_chunk (chunk_id, obligation_id, section_id, chunk_text, embedding, tsv)
                   values (%(cid)s,%(oid)s,%(sec)s,%(text)s,%(emb)s::vector,to_tsvector('english',%(text)s))
                   on conflict (chunk_id) do update set
                     chunk_text=excluded.chunk_text, embedding=excluded.embedding, tsv=excluded.tsv;""",
                {"cid": f"{o['suggested_id']}-c1", "oid": o["suggested_id"], "sec": sec["section_id"],
                 "text": o["obligation_text"], "emb": to_pgvector(vec)},
            )
    print(f"  {path.name}: loaded {len(obligations)} obligations, {len(b['relations'])} edges")
    return len(obligations), len(b["relations"]), len(obligations)


def main(argv: list[str]) -> int:
    include_unapproved = "--include-unapproved" in argv
    nums = [a for a in argv if a.isdigit()]
    if nums:
        paths = [REVIEW_DIR / f"chapter_{n}_bundle.json" for n in nums]
    else:
        paths = sorted(REVIEW_DIR.glob("chapter_*_bundle.json"))
    print(f"Loading {len(paths)} bundle(s) (approved {'+ unapproved' if include_unapproved else 'only'})...")
    for p in paths:
        if p.exists():
            load_bundle(p, include_unapproved)

    with get_cursor() as cur:
        cur.execute("select count(*) n from adj_obligation where is_synthetic=false;")
        n_ob = cur.fetchone()["n"]
        cur.execute("select count(*) n from adj_obligation_relations;")
        n_rel = cur.fetchone()["n"]
        cur.execute("select count(*) n from adj_obligation_chunk where embedding is not null;")
        n_emb = cur.fetchone()["n"]
    print(f"\nTotals: real obligations={n_ob}, relation edges={n_rel}, embedded chunks={n_emb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
