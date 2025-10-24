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

# Database setup
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def clean_database() -> None:
    """Remove all data from the database while preserving schema."""
    db = SessionLocal()
    try:
        print("🧹 Starting database cleanup...")
        print("⚠️  WARNING: This will delete ALL data from your database!")

        # Get confirmation from user
        response = input("Are you sure you want to continue? (yes/no): ").lower().strip()
        if response not in ["yes", "y"]:
            print("❌ Cleanup cancelled.")
            return

        print("\n🗑️  Removing data from all tables...")

        # Clear data in correct order (respecting foreign key constraints)
        tables_to_clear = [
            "submissions",  # Has foreign keys to sessions and students
            "sessions",  # Has foreign keys to courses and surveys
            "courses",  # Has foreign keys to teachers
            "students",  # Independent table
            "teachers",  # Independent table
            "surveys",  # Independent table (survey templates)
        ]

        cleared_count = {}

        for table in tables_to_clear:
            try:
                # Count records before deletion
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count_before = count_result.scalar() or 0

                # Delete all records
                db.execute(text(f"DELETE FROM {table}"))

                cleared_count[table] = count_before
                print(f"✅ Cleared {count_before} records from {table}")

            except Exception as e:
                print(f"⚠️  Warning: Could not clear {table}: {e}")
                cleared_count[table] = 0

        # Commit all changes
        db.commit()

        print("\n🎉 Database cleanup completed!")
        print("\n📊 Summary of cleared data:")
        total_cleared = 0
        for table, count in cleared_count.items():
            if count > 0:
                print(f"  - {table}: {count} records")
                total_cleared += count

        if total_cleared == 0:
            print("  - No data was found to clear (database was already empty)")
        else:
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

        tables_to_check = ["teachers", "students", "courses", "surveys", "sessions", "submissions"]

        total_records = 0
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar() or 0
                print(f"  - {table}: {count} records")
                total_records += count
            except Exception as e:
                print(f"  - {table}: Error checking ({e})")

        print(f"\nTotal records in database: {total_records}")

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
        # Override the confirmation in clean_database
        import builtins

        original_input = builtins.input
        builtins.input = lambda _: "yes"  # type: ignore[assignment]
        try:
            clean_database()
        finally:
            builtins.input = original_input
    else:
        clean_database()


if __name__ == "__main__":
    main()
