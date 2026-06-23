"""Apply a SQL migration to the shared Supabase project.

Only touches the isolated `adjudicator` schema. Idempotent (uses
create ... if not exists / create or replace throughout).

Usage:  python scripts/apply_migration.py supabase/migrations/001_schema.sql
"""
import sys
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from app.config import settings  # noqa: E402


def main(path: str) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    conn = psycopg2.connect(settings.database_url)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"Applied {path} to schema '{settings.db_schema}'.")
    finally:
        conn.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "supabase/migrations/001_schema.sql"
    main(str(ROOT / target))
