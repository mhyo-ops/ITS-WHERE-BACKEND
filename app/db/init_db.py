from __future__ import annotations

from sqlalchemy import text

from .base import engine


def init_db() -> None:
    """
    Verify database connection on startup.
    Schema is managed by Alembic — do not call create_all here.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection verified")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


if __name__ == "__main__":
    init_db()
