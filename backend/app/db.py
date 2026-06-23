"""Thin psycopg2 access to the isolated adjudicator schema.

Every connection sets search_path to the app schema (+ extensions for the
vector type), so callers never have to qualify table names.
"""
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from .config import settings


@contextmanager
def get_conn():
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"set search_path to {settings.db_schema}, extensions, public;"
            )
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(commit: bool = False):
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
