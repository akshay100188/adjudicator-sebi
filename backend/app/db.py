"""psycopg2 access to the isolated adjudicator schema.

A single warm connection is reused across calls (single-process app + eval). This avoids
a fresh TCP+TLS+auth handshake to the remote Supabase pooler on every query — the dominant
latency in EXP-001. autocommit is on, so each statement is its own transaction (reads need no
commit; idempotent upserts apply immediately; an error doesn't poison later statements).
"""
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from .config import settings

_conn = None


def _shared_conn():
    global _conn
    if _conn is None or getattr(_conn, "closed", 1):
        _conn = psycopg2.connect(settings.database_url)
        _conn.autocommit = True
        with _conn.cursor() as cur:
            cur.execute(f"set search_path to {settings.db_schema}, extensions, public;")
    return _conn


@contextmanager
def get_conn():
    """Yield the shared connection (kept open for reuse)."""
    yield _shared_conn()


@contextmanager
def get_cursor(commit: bool = False):  # commit kept for signature compatibility (autocommit on)
    conn = _shared_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield cur
    finally:
        cur.close()
