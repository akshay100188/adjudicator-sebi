"""Phase 2 ingestion (extraction stage) — one or more chapters.

Parse → build relation edges → LLM-extract obligations → write a REVIEW bundle per chapter.
Stops before DB load: a human reviews/edits each bundle first (ADR-009). Reviewed bundles are
loaded + embedded by scripts/ingest_load.py.

Usage:
  python scripts/ingest_chapter.py            # all chapters in the registry
  python scripts/ingest_chapter.py 45 46      # only the listed chapters
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.ingest.parse import parse_chapter         # noqa: E402
from app.ingest.relations import build_edges        # noqa: E402
from app.ingest.extract import extract_obligations   # noqa: E402

MASTER = {
    "circular_ref": "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/110",
    "issue_date": "2024-08-09",
    "source_url": "https://www.sebi.gov.in/legal/master-circulars/aug-2024/master-circular-for-stock-brokers_85605.html",
    "pdf": "data/raw/sb_master_2024-08-09.pdf",
}
PRIOR_MASTER_REF = "SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2024/53"

# chapter_no -> (page_start, page_end). page_end = next chapter's start page (parser cuts at "N+1.").
CHAPTER_SPECS = {
    45: (117, 119),   # Handling of Client's Securities
    46: (119, 121),   # Validation of Pay-In of Securities from Client demat
    47: (121, 123),   # Settlement of Running Account (already loaded)
    92: (229, 230),   # Bank Guarantees out of clients' funds
    93: (230, 233),   # Upstreaming of clients' funds
}

OUT_DIR = ROOT / "data" / "obligations" / "review"


def process(chapter_no: int, with_supersedes: bool) -> dict:
    ps, pe = CHAPTER_SPECS[chapter_no]
    chapter = parse_chapter(ROOT / MASTER["pdf"], chapter_no, ps, pe)
    print(f"ch {chapter_no}: {chapter.heading[:55]} — {len(chapter.clauses)} clauses, "
          f"{len(chapter.source_refs)} source refs")
    edges = build_edges(chapter, MASTER["circular_ref"],
                        PRIOR_MASTER_REF if with_supersedes else None)
    obligations = extract_obligations(chapter)
    for o in obligations:
        o["_approved"] = False
    print(f"   -> {len(obligations)} candidate obligations, {len(edges)} edges")

    bundle = {
        "master": MASTER, "prior_master_ref": PRIOR_MASTER_REF,
        "chapter": {
            "chapter_no": chapter.chapter_no, "heading": chapter.heading,
            "page_span": [ps, pe],
            "source_refs": [{"circular_ref": r.circular_ref, "dated": r.dated} for r in chapter.source_refs],
        },
        "parent_section": {
            "section_id": f"SB-CH{chapter.chapter_no}", "circular_ref": MASTER["circular_ref"],
            "heading": chapter.heading, "full_text": chapter.full_text,
        },
        "obligations": obligations, "relations": edges,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"chapter_{chapter_no}_bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_review_md(bundle)
    return bundle


def _write_review_md(bundle: dict) -> None:
    ch = bundle["chapter"]
    lines = [
        f"# Review — Chapter {ch['chapter_no']}: {ch['heading']}", "",
        f"Source (current): `{bundle['master']['circular_ref']}` ({bundle['master']['issue_date']})  ",
        "Consolidates: " + ", ".join(f"`{r['circular_ref']}` ({r['dated']})" for r in ch["source_refs"]),
        "", "> Not legal advice. Approve/correct each obligation, then set `_approved: true`.", "",
        f"## Candidate obligations ({len(bundle['obligations'])})",
    ]
    for o in bundle["obligations"]:
        lines += [
            f"\n### {o['suggested_id']} — {o['title']}",
            f"- **Clauses:** {', '.join(o['clause_refs'])}",
            f"- **Category:** {o['category']} · **Intermediary:** {o['intermediary_type']}",
            f"- **Obligation:** {o['obligation_text']}",
            f"- **Expected controls:** {'; '.join(o['expected_controls'])}",
        ]
    lines += ["", f"## Relation edges ({len(bundle['relations'])})", ""]
    for e in bundle["relations"]:
        lines.append(f"- `{e['from_ref']}` --{e['relation_type']}--> `{e['to_ref']}`  ({e['source_note']})")
    (OUT_DIR / f"chapter_{ch['chapter_no']}_REVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    chapters = [int(a) for a in argv] if argv else sorted(CHAPTER_SPECS)
    print(f"Ingesting chapters: {chapters}\n")
    for i, n in enumerate(chapters):
        process(n, with_supersedes=(i == 0))  # supersedes edge once is enough (idempotent anyway)
    print(f"\nReview bundles in {OUT_DIR}. Edit _approved, then run ingest_load.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
