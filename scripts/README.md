# Scripts Directory

This directory contains utility scripts for database management and development tasks.

## Available Scripts

### `clean_db.py` – database cleanup

Truncates every application table (`Base.metadata`) while keeping the schema intact. Designed for
repeatable local resets.

#### Highlights

- **Metadata-driven**: Builds the truncate statement dynamically so new tables are included
  automatically (no manual list).
- **Identity reset**: Uses `TRUNCATE ... RESTART IDENTITY CASCADE` to reset primary keys.
- **Confirmation prompt**: Prevents accidental wipes (use `--force` for automation).
- **Status mode**: `--check` returns record counts without modifying the DB.

#### Usage

```bash
# Check database state (safe, read-only)
uv run python scripts/clean_db.py --check
make db-status

# Clean database with confirmation prompt
uv run python scripts/clean_db.py
make db-clean

# Force clean without confirmation (use with caution!)
uv run python scripts/clean_db.py --force
make db-clean-force
```

#### What it does
1. Prints a summary of all tracked tables and their row counts (via `--check`).
2. Prompts for confirmation (unless `--force`).
3. Executes a single `TRUNCATE ... RESTART IDENTITY CASCADE` statement covering every application
   table except `alembic_version`.
4. Prints per-table counts removed and the total number of affected rows.
5. Suggests re-seeding next steps.

#### Example Output

```
🧹 Starting database cleanup...
⚠️  WARNING: This will delete ALL data from your database!

Are you sure you want to continue? (yes/no): yes

🗑️  Removing data from all tables...
✅ Cleared 3 records from submissions
✅ Cleared 2 records from sessions
✅ Cleared 1 records from courses
✅ Cleared 2 records from students
✅ Cleared 1 records from teachers
✅ Cleared 2 records from surveys

🎉 Database cleanup completed!

📊 Summary of cleared data:
  - submissions: 3 records
  - sessions: 2 records
  - courses: 1 records
  - students: 2 records
  - teachers: 1 records
  - surveys: 2 records

Total records cleared: 11

💡 Next steps:
  - Run 'uv run python scripts/seed.py' to populate with sample data
  - Or start fresh with your own data
```

### `seed.py` – database seeding

Populates the database with end-to-end sample data:

- Teacher + student accounts with hashed passwords.
- Two detailed survey templates (Learning Buddy & Critter Quest).
- A course, sessions (one requiring rebaseline), submissions, and participant profiles.
- Default activity types and example activities usable across courses.
- Course recommendations that exercise the fallback chain.

#### Usage

```bash
# Seed database with sample data
uv run python scripts/seed.py
make db-seed            # automatically runs `make db-clean` first
```

### `seed_deploy_test.py` – minimal deploy-test dataset

Clears existing data and inserts only the shared catalog assets:

- the two legacy survey templates (Critter Quest + Learning Buddy)
- default activity types
- default activities for those types

No teachers, courses, sessions, or recommendations are created.

#### Usage

```bash
# Seed database with catalog-only content
uv run python scripts/seed_deploy_test.py
make db-seed seed_deploy_test.py
```

### `check_db_state.py` – schema sanity check

Confirms that every ORM-managed table exists and shows row counts. Useful after migrations or a
cleanup.

#### Usage

```bash
# Check database state
uv run python scripts/check_db_state.py
make db-check
```

## Makefile Integration

All scripts are integrated with the Makefile for easy access:

```bash
# Database management
make db-status                 # Show database record counts
make db-clean                  # Clean all data (with confirmation)
make db-clean-force            # Force clean all data (no confirmation)
make db-seed [script.py]       # Clean + seed (default uses scripts/seed.py)
make db-check                  # Check database state
make db-migrate                # Run database migrations
```

## Safety Features

### Confirmation Prompts
- The clean script always asks for confirmation before deleting data
- Use `--force` flag only in automated scripts where confirmation isn't possible

### Cascade-safe
- Uses `TRUNCATE ... CASCADE` so dependent rows are removed automatically
- Prevents orphaned records or constraint violations even as the schema grows

### Error Handling
- Graceful error handling with rollback on failures
- Clear error messages and suggestions

### Read-Only Operations
- `--check` flag allows safe inspection without any modifications
- Status commands are completely safe to run

## Development Workflow

### Typical Development Cycle

```bash
# 1. Check current state
make db-status

# 2. Clean if needed
make db-clean

# 3. Re-seed with fresh data (auto-cleans first)
make db-seed              # default seed data
# or keep only surveys + activity catalog
make db-seed seed_deploy_test.py

# 4. Test your changes
make test
```

### Testing New Features

```bash
# Clean slate for testing
make db-clean-force
make db-seed              # cleans + seeds automatically
# or seed only catalog fixtures
make db-seed seed_deploy_test.py

# Test your feature
# ... your testing ...

# Clean up after testing
make db-clean
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose up -d database`
- Check database URL in `.env` file
- Verify migrations are up to date: `make db-migrate`

### Permission Issues
- Ensure the script is executable: `chmod +x scripts/clean_db.py`
- Check database user permissions

### Data Recovery
- If you accidentally clean important data, restore from backup: `make db-backup`
- Or re-seed with sample data: `make db-seed`
