"""Privacy-safe code scanner (Phase 8 stretch).

Extracts compliance-relevant SIGNALS from a repo — file path, line, a category, and a short
description — and NEVER retains or transmits the code itself. Two layers: regex pattern rules
(any language) + a Python-AST layer (financial fund-movement functions missing an audit trail).
Semgrep is an optional third layer (not required; absent here).

These signals are metadata only. They feed the same agent→synthesis engine to map to SEBI obligations.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SCAN_EXT = {".py", ".js", ".ts", ".java", ".go", ".rb"}
MAX_BYTES = 400_000


@dataclass
class CodeSignal:
    file: str
    line: int
    category: str
    description: str


# (compiled regex, category, human description). Targeted at stock-broker systems.
PATTERN_RULES: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"\b(pool(ed)?|house|own)[_ ]?(client[_ ]?)?(funds|money|account)\b", re.I),
     "client_funds_pooling",
     "client funds appear to be held/pooled in a non-designated (house/own) account rather than a nodal account"),
    (re.compile(r"\b(log|logger|logging|print|console\.log)\b.{0,40}\b(pan|aadha?ar|account[_ ]?number|client[_ ]?id|dob)\b", re.I),
     "pii_logging",
     "client PII (PAN/Aadhaar/account number) appears to be written to logs"),
    (re.compile(r"\b(api[_ ]?key|secret|password|passwd|token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{8,}['\"]", re.I),
     "hardcoded_secret",
     "a hardcoded secret/credential appears in source"),
    (re.compile(r"settle\w*.{0,30}(annual|yearly|once[_ ]a[_ ]year)|SETTLEMENT[_ ](PERIOD|DAYS|FREQ\w*)\s*[:=]\s*(['\"]?(annual|yearly)|36[05])", re.I),
     "settlement_frequency",
     "running-account settlement appears to run annually rather than monthly/quarterly"),
    (re.compile(r"\b(delete|drop|truncate|purge)\b.{0,30}\b(audit|transaction|trade|record|ledger)\b", re.I),
     "record_deletion",
     "code deletes/purges audit or transaction records (retention concern)"),
    (re.compile(r"authorized[_ ]?person.{0,40}(receive|accept|collect).{0,20}(funds|money|securities)", re.I),
     "authorized_person_funds",
     "an authorised person appears to accept client funds/securities"),
]


def _scan_text(rel: str, text: str) -> list[CodeSignal]:
    out: list[CodeSignal] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for rx, cat, desc in PATTERN_RULES:
            if rx.search(line):
                out.append(CodeSignal(rel, i, cat, desc))
    return out


# Python AST: fund-movement functions with no audit/log call in the body.
FUND_FN = re.compile(r"transfer|settle|payout|pay_in|payin|withdraw|upstream|disburse|remit", re.I)
AUDIT_CALL = re.compile(r"audit|log|record_event|trail", re.I)


def _scan_python_ast(rel: str, text: str) -> list[CodeSignal]:
    out: list[CodeSignal] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and FUND_FN.search(node.name):
            body_src = " ".join(
                n.func.attr if isinstance(getattr(n, "func", None), ast.Attribute)
                else (n.func.id if isinstance(getattr(n, "func", None), ast.Name) else "")
                for n in ast.walk(node) if isinstance(n, ast.Call)
            )
            if not AUDIT_CALL.search(body_src):
                out.append(CodeSignal(
                    rel, node.lineno, "missing_audit_trail",
                    f"fund-movement function '{node.name}()' has no audit/log call (audit-trail concern)",
                ))
    return out


def scan_repo(root: str | Path) -> tuple[list[CodeSignal], dict]:
    """Returns (signals, meta). meta = files_scanned, languages. Code is never retained."""
    root = Path(root)
    signals: list[CodeSignal] = []
    files = 0
    langs: set[str] = set()
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in SCAN_EXT:
            continue
        if any(part in {"node_modules", ".git", ".venv", "venv", "dist", "build"} for part in p.parts):
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files += 1
        langs.add(p.suffix.lstrip("."))
        rel = str(p.relative_to(root)).replace("\\", "/")
        signals += _scan_text(rel, text)
        if p.suffix == ".py":
            signals += _scan_python_ast(rel, text)
        del text  # do not retain code
    return signals, {"files_scanned": files, "languages": sorted(langs)}
