#!/usr/bin/env python3
"""
Database Cleanup Script

This script removes all data from the database while preserving the schema.
Useful for testing and development when you need a clean slate.

⚠️  WARNING: This will delete ALL data from your database!
"""

import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust path to import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from app.models import Base  # noqa: E402

# Database setup
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _collect_table_names() -> list[str]:
    """Return all ORM-managed table names excluding Alembic metadata."""
    table_names = [
        table.name for table in Base.metadata.sorted_tables if table.name != "alembic_version"
    ]
    if not table_names:
        raise RuntimeError("No ORM tables discovered; has app.models been imported?")
    return table_names


def clean_database(force: bool = False) -> None:
    """Remove all data from application tables while preserving schema."""
    db = SessionLocal()
    try:
        print("🧹 Starting database cleanup...")
        print("⚠️  WARNING: This will delete ALL application data from your database!")

        if not force:
            response = input("Are you sure you want to continue? (yes/no): ").lower().strip()
            if response not in {"yes", "y"}:
                print("❌ Cleanup cancelled.")
                return

        print("\n🗑️  Removing data from all application tables...")

        tables = _collect_table_names()
        cleared_counts: dict[str, int] = {}

        for name in tables:
            try:
                result = db.execute(text(f'SELECT COUNT(*) FROM "{name}"'))
                cleared_counts[name] = result.scalar() or 0
            except Exception:
                cleared_counts[name] = 0

        truncate_sql = "TRUNCATE TABLE {} RESTART IDENTITY CASCADE".format(
            ", ".join(f'"{name}"' for name in tables)
        )
        db.execute(text(truncate_sql))
        db.commit()

        print("\n🎉 Database cleanup completed!")
        print("\n📊 Summary of cleared data:")
        total_cleared = 0
        for table_name in tables:
            count = cleared_counts.get(table_name, 0)
            print(f"  - {table_name}: {count} records removed")
            total_cleared += count

        print(f"\nTotal records cleared: {total_cleared}")
        print("\n💡 Next steps:")
        print("  - Run 'uv run python scripts/seed.py' to populate with sample data")
        print("  - Or start fresh with your own data")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_database_state() -> None:
    """Check the current state of the database."""
    db = SessionLocal()
    try:
        print("🔍 Checking database state...")

        tables_to_check = _collect_table_names()

        total_records = 0
        for table in tables_to_check:
            try:
                result = db.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                count = result.scalar() or 0
                print(f"  - {table}: {count} records")
                total_records += count
            except Exception as e:
                print(f"  - {table}: Error checking ({e})")

        print(f"\nTotal records across tracked tables: {total_records}")

        if total_records == 0:
            print("✅ Database is empty")
        else:
            print("📊 Database contains data")

    except Exception as e:
        print(f"❌ Error checking database state: {e}")
    finally:
        db.close()


def main() -> None:
    """Main function with command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Database cleanup utility")
    parser.add_argument(
        "--check", action="store_true", help="Check database state without cleaning"
    )
    parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt (use with caution!)"
    )

    args = parser.parse_args()

    if args.check:
        check_database_state()
        return

    if args.force:
        print("🧹 Force cleaning database (skipping confirmation)...")
        clean_database(force=True)
    else:
        clean_database(force=False)


if __name__ == "__main__":
    main()
