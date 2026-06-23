"""Phase 2 load stage: persist the reviewed bundle into adj_ tables + embed chunks.

Loads ONLY obligations flagged `_approved: true` (the human-review gate, ADR-009),
unless --all is passed. Idempotent (upserts). Run after editing the review bundle.

Usage:
  python scripts/ingest_load.py                 # approved obligations only
  python scripts/ingest_load.py --all           # load all candidates (e.g. demo)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.db import get_cursor                       # noqa: E402
from app.ingest.embed import embed_texts, to_pgvector  # noqa: E402

BUNDLE = ROOT / "data" / "obligations" / "review" / "chapter_47_bundle.json"


def main(load_all: bool) -> int:
    b = json.loads(BUNDLE.read_text(encoding="utf-8"))
    master, sec = b["master"], b["parent_section"]
    obligations = [o for o in b["obligations"] if load_all or o.get("_approved")]
    if not obligations:
        print("No approved obligations. Set _approved=true in the bundle, or pass --all.")
        return 1
    print(f"Loading {len(obligations)} obligations (of {len(b['obligations'])} candidates)...")

    with get_cursor(commit=True) as cur:
        # Parent section
        cur.execute(
            """insert into adj_obligation_section (section_id, circular_ref, heading, full_text)
               values (%(section_id)s, %(circular_ref)s, %(heading)s, %(full_text)s)
               on conflict (section_id) do update set
                 heading = excluded.heading, full_text = excluded.full_text;""",
            sec,
        )
        # Obligations
        for o in obligations:
            cur.execute(
                """insert into adj_obligation
                     (obligation_id, obligation_text, source_circular_ref, source_url,
                      issue_date, effective_date, superseded_by, regulation_family,
                      intermediary_type, category, parent_section_id, is_synthetic,
                      title, clause_refs, expected_controls)
                   values
                     (%(oid)s, %(text)s, %(cref)s, %(url)s, %(idate)s, %(idate)s, NULL,
                      'stock_brokers', %(itype)s, %(cat)s, %(sec)s, false,
                      %(title)s, %(clauses)s, %(controls)s)
                   on conflict (obligation_id) do update set
                     obligation_text = excluded.obligation_text,
                     title = excluded.title,
                     clause_refs = excluded.clause_refs,
                     expected_controls = excluded.expected_controls,
                     category = excluded.category,
                     intermediary_type = excluded.intermediary_type;""",
                {
                    "oid": o["suggested_id"], "text": o["obligation_text"],
                    "cref": master["circular_ref"], "url": master["source_url"],
                    "idate": master["issue_date"], "itype": o.get("intermediary_type"),
                    "cat": o.get("category"), "sec": sec["section_id"],
                    "title": o.get("title"), "clauses": o.get("clause_refs"),
                    "controls": json.dumps(o.get("expected_controls", [])),
                },
            )
        # Relations
        for e in b["relations"]:
            cur.execute(
                """insert into adj_obligation_relations (from_ref, to_ref, relation_type, source_note)
                   values (%(from_ref)s, %(to_ref)s, %(relation_type)s, %(source_note)s)
                   on conflict (from_ref, to_ref, relation_type) do nothing;""",
                e,
            )

    # Chunks + embeddings (one clause-grain chunk per obligation).
    print("Embedding chunks (OpenAI text-embedding-3-small @512)...")
    vectors = embed_texts([o["obligation_text"] for o in obligations])
    with get_cursor(commit=True) as cur:
        for o, vec in zip(obligations, vectors):
            cur.execute(
                """insert into adj_obligation_chunk
                     (chunk_id, obligation_id, section_id, chunk_text, embedding, tsv)
                   values (%(cid)s, %(oid)s, %(sec)s, %(text)s, %(emb)s::vector,
                           to_tsvector('english', %(text)s))
                   on conflict (chunk_id) do update set
                     chunk_text = excluded.chunk_text,
                     embedding = excluded.embedding,
                     tsv = excluded.tsv;""",
                {
                    "cid": f"{o['suggested_id']}-c1", "oid": o["suggested_id"],
                    "sec": b["parent_section"]["section_id"], "text": o["obligation_text"],
                    "emb": to_pgvector(vec),
                },
            )

    with get_cursor() as cur:
        cur.execute("select count(*) n from adj_obligation where is_synthetic=false;")
        n_ob = cur.fetchone()["n"]
        cur.execute("select count(*) n from adj_obligation_relations;")
        n_rel = cur.fetchone()["n"]
        cur.execute("select count(*) n from adj_obligation_chunk where embedding is not null;")
        n_emb = cur.fetchone()["n"]
    print(f"Done. real obligations={n_ob}, relation edges={n_rel}, embedded chunks={n_emb}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--all" in sys.argv[1:]))
