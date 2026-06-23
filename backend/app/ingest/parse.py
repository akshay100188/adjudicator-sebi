"""Structure-aware parsing of a SEBI master-circular chapter (ADR-007: clause grain).

Given a master-circular PDF + an explicit chapter spec (number + page range), extract:
  - the parent section (full chapter text + heading),
  - ordered clauses keyed by their SEBI clause number (e.g. 47.1, 47.1.1),
  - the footnote source-circular references that cite the originating circulars.

Page ranges are explicit and recorded in data/obligations/seed_manifest.md so the
parse is reproducible (a crawler/heuristic chapter detector is out of scope — ADR-008).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

# Matches SEBI circular references like SEBI/HO/MIRSD/DOP/P/CIR/2022/101
CIRCULAR_REF = re.compile(r"SEBI/[A-Za-z0-9/_\-]+/CIR/\d{4}/\d+", re.I)
# Footnote definition line: "63 Reference: Circular SEBI/... dated June 16, 2021, Circular ..."
FOOTNOTE_DATE = re.compile(
    r"dated\s+([A-Z][a-z]+ \d{1,2},?\s*\d{4})", re.I
)


def _clean(t: str) -> str:
    """Fix the common pypdf encoding artifacts in SEBI PDFs."""
    return (t or "").replace("�", "'").replace("\x92", "'").replace("’", "'")


@dataclass
class SourceRef:
    circular_ref: str
    dated: str | None = None


@dataclass
class Clause:
    clause_no: str          # "47.1.1"
    text: str


@dataclass
class ParsedChapter:
    chapter_no: int
    heading: str
    full_text: str
    clauses: list[Clause] = field(default_factory=list)
    source_refs: list[SourceRef] = field(default_factory=list)


def parse_chapter(
    pdf_path: str | Path,
    chapter_no: int,
    page_start: int,
    page_end: int,
) -> ParsedChapter:
    """Extract one chapter. page_start/page_end are 0-based PDF page indices, inclusive."""
    reader = PdfReader(str(pdf_path))
    pages = [_clean(reader.pages[i].extract_text() or "") for i in range(page_start, page_end + 1)]
    raw = "\n".join(pages)

    # Heading: the "<n>. <Title>" line that opens the chapter.
    heading = ""
    m = re.search(rf"(?m)^\s*{chapter_no}\.\s+(.+)$", raw)
    if m:
        heading = re.sub(rf"\d+\s*$", "", m.group(1)).strip()  # drop trailing footnote marker

    # Body runs from the chapter heading to the next top-level chapter "<n+1>."
    start = m.start() if m else 0
    nxt = re.search(rf"(?m)^\s*{chapter_no + 1}\.\s+\S", raw[start + 1:])
    body = raw[start: start + 1 + nxt.start()] if nxt else raw[start:]

    # Footnote source references (definitions like "63 Reference: Circular SEBI/... dated ...").
    # Scope to `body` (heading → next chapter) so a later chapter's footnote isn't attributed here.
    refs: list[SourceRef] = []
    for fm in re.finditer(r"(?m)^\s*\d{1,3}\s+Reference:(.+?)(?=\n\s*\n|\Z)", body, re.S):
        block = fm.group(1)
        dates = FOOTNOTE_DATE.findall(block)
        for j, cref in enumerate(CIRCULAR_REF.findall(block)):
            refs.append(SourceRef(circular_ref=cref, dated=dates[j] if j < len(dates) else None))
    # De-dup, preserve order.
    seen: set[str] = set()
    refs = [r for r in refs if not (r.circular_ref in seen or seen.add(r.circular_ref))]

    # Clause split on SEBI clause numbers at line start (47, 47.1, 47.1.1 ...).
    marker = re.compile(rf"(?m)^\s*({chapter_no}(?:\.\d+)+)\s+")
    hits = list(marker.finditer(body))
    clauses: list[Clause] = []
    for i, hit in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        text = body[hit.end():end].strip()
        text = re.sub(r"\s*\n\s*", " ", text)          # unwrap soft line breaks
        text = re.sub(r"\s{2,}", " ", text).strip()
        # Drop footnote-definition tails that leaked into the last clause.
        text = re.split(r"\s+\d{1,3}\s+Reference:", text)[0].strip()
        if text:
            clauses.append(Clause(clause_no=hit.group(1), text=text))

    return ParsedChapter(
        chapter_no=chapter_no,
        heading=heading,
        full_text=re.sub(r"\n{3,}", "\n\n", body).strip(),
        clauses=clauses,
        source_refs=refs,
    )
