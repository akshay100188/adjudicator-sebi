"""Code-analysis pipeline (Phase 8).

scan → render privacy-safe signals as a textual description → feed the SAME agent→synthesis engine
→ cited SEBI obligation findings. The code is never sent to the LLM or stored; only the derived
signal metadata (file path, line, category, description) flows downstream.

Privacy-by-design for GitHub: shallow clone → scan → delete; persist only finding metadata.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

from ..agent.agent import DISCLAIMER
from ..synthesis.synthesize import analyze_scenario
from .scanner import CodeSignal, scan_repo

# Repo root (parent of backend/), so relative demo paths resolve regardless of the server's cwd.
_ROOT = Path(__file__).resolve().parents[3]


def _render(signals: list[CodeSignal]) -> str:
    """Turn signals into a practice description the agent can map to obligations (metadata only)."""
    by_cat: dict[str, list[CodeSignal]] = {}
    for s in signals:
        by_cat.setdefault(s.category, []).append(s)
    lines = ["Static analysis of a stock-broker codebase surfaced the following implemented practices:"]
    for cat, group in by_cat.items():
        locs = ", ".join(f"{g.file}:{g.line}" for g in group[:5])
        lines.append(f"- {group[0].description} (at {locs}).")
    return "\n".join(lines)


def analyse_path(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = _ROOT / p  # resolve relative demo paths against the repo root
    signals, meta = scan_repo(p)
    meta["scanned_path"] = str(p)
    if not signals:
        return {**meta, "signals": [], "findings": [],
                "note": "No compliance-relevant code signals detected.", "disclaimer": DISCLAIMER}
    description = _render(signals)
    result = analyze_scenario(description)
    return {
        **meta,
        "signals": [asdict(s) for s in signals],
        "derived_description": description,
        **result,  # route, findings, trajectory, obligations_considered, disclaimer, ...
    }


def analyse_github(url: str) -> dict:
    """Shallow clone → scan → delete. Only finding metadata survives."""
    tmp = tempfile.mkdtemp(prefix="adj_scan_")
    try:
        subprocess.run(["git", "clone", "--depth", "1", url, tmp],
                       check=True, capture_output=True, timeout=120)
        return analyse_path(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)  # code never persisted
