#!/usr/bin/env python3
"""
Database State Checker

This script helps verify the current database state and prevents confusion
between 'surveys' and 'survey_templates' tables.

Usage:
    uv run python scripts/check_db_state.py
"""

import sys
from pathlib import Path

from sqlalchemy import text

# Adjust path to import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.db import get_db  # noqa: E402


def check_database_state():
    """Check the current state of the database and report any issues."""
    print("🔍 Checking database state...")
    print("=" * 50)

    db = next(get_db())

    try:
        # Check all tables
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
        tables = [row[0] for row in result]

        print("📋 Current tables:")
        for table in tables:
            print(f"  ✅ {table}")

        print()

        # Check for survey-related tables

        if "surveys" in tables and "survey_templates" in tables:
            print("⚠️  WARNING: Both 'surveys' and 'survey_templates' tables exist!")
            print("   This indicates a migration issue.")
            print("   Run the emergency recovery script in README.md")
            return False

        elif "survey_templates" in tables and "surveys" not in tables:
            print("❌ ERROR: Only 'survey_templates' table exists!")
            print("   The table should be renamed to 'surveys'.")
            print("   Run: uv run alembic upgrade head")
            return False

        elif "surveys" in tables and "survey_templates" not in tables:
            print("✅ CORRECT: 'surveys' table exists, 'survey_templates' is gone.")

        else:
            print("❌ ERROR: No survey tables found!")
            print("   Run: uv run alembic upgrade head")
            return False

        # Check foreign key constraints
        print()
        print("🔗 Checking foreign key constraints...")
        result = db.execute(
            text(
                """
            SELECT 
                tc.constraint_name, 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND tc.table_name = 'sessions'
              AND kcu.column_name LIKE '%survey%';
        """
            )
        )

        constraints = list(result)
        if constraints:
            print("   Foreign key constraints:")
            for constraint, table, column, foreign_table, foreign_column in constraints:
                if foreign_table == "surveys":
                    print(
                        f"   ✅ {constraint}: {table}.{column} -> {foreign_table}.{foreign_column}"
                    )
                else:
                    print(
                        f"   ❌ {constraint}: {table}.{column} -> {foreign_table}.{foreign_column} "
                        f"(should be 'surveys')"
                    )
        else:
            print("   ❌ No foreign key constraints found for sessions table")
            return False

        # Check survey data
        print()
        print("📊 Checking survey data...")
        result = db.execute(text("SELECT COUNT(*) FROM surveys;"))
        count = result.scalar()
        print(f"   Surveys in database: {count}")

        if count > 0:
            # Check for sample surveys
            result = db.execute(text("SELECT title FROM surveys LIMIT 3;"))
            titles = [row[0] for row in result]
            print("   Sample surveys:")
            for title in titles:
                print(f"     - {title}")

        print()
        print("✅ Database state is correct!")
        print("   All survey operations should use the 'surveys' table.")
        return True

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = check_database_state()
    sys.exit(0 if success else 1)
