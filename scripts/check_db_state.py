#!/usr/bin/env python3
"""
Database state checker for dev environment.

Usage: uv run python scripts/check_db_state.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Adjust path to import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.db import get_db  # noqa: E402
from app.models import Base  # noqa: E402


def _expected_tables() -> list[str]:
    return [table.name for table in Base.metadata.sorted_tables if table.name != "alembic_version"]


def check_database_state() -> bool:
    """Check the current state of the database and report any issues."""
    print("🔍 Checking database state...")
    print("=" * 50)

    db = next(get_db())

    try:
        result = db.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
            )
        )
        existing_tables = {row[0] for row in result}

        expected = _expected_tables()

        print("📋 Expected application tables:")
        for table in expected:
            marker = "✅" if table in existing_tables else "❌"
            print(f"  {marker} {table}")

        missing = [table for table in expected if table not in existing_tables]
        unexpected = sorted(existing_tables - set(expected) - {"alembic_version"})

        if missing:
            print("\n❌ Missing tables detected:")
            for table in missing:
                print(f"   - {table}")
            print("   Run migrations: uv run alembic upgrade head")
            return False

        if unexpected:
            print("\n⚠️  Unexpected tables detected (verify these are intentional):")
            for table in unexpected:
                print(f"   - {table}")

        print("\n📊 Row counts:")
        total_records = 0
        for table in expected:
            try:
                count = db.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar() or 0
                print(f"  - {table}: {count}")
                total_records += count
            except Exception as exc:
                print(f"  - {table}: error retrieving count ({exc})")

        print(f"\nTotal records across tracked tables: {total_records}")
        print("\n✅ Database state check complete.")
        return True

    except Exception as exc:
        print(f"❌ Error checking database: {exc}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = check_database_state()
    sys.exit(0 if success else 1)
