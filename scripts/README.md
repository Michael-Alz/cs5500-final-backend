# Scripts Directory

This directory contains utility scripts for database management and development tasks.

## Available Scripts

### `clean_db.py` - Database Cleanup Script

A comprehensive script to clean all data from your database while preserving the schema.

#### Features
- **Safe Cleanup**: Removes all data while preserving database structure
- **Foreign Key Aware**: Clears tables in the correct order to respect constraints
- **Confirmation Prompt**: Asks for confirmation before deleting data
- **Status Checking**: Can check database state without cleaning
- **Force Mode**: Skip confirmation for automated scripts

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
1. **Checks database state** - Shows record counts for all tables
2. **Asks for confirmation** - Prevents accidental data loss
3. **Clears data in order** - Respects foreign key constraints:
   - `submissions` (has foreign keys to sessions and students)
   - `sessions` (has foreign keys to courses and surveys)
   - `courses` (has foreign keys to teachers)
   - `students` (independent table)
   - `teachers` (independent table)
   - `surveys` (independent table)
4. **Provides summary** - Shows how many records were cleared
5. **Suggests next steps** - Recommends re-seeding if needed

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

### `seed.py` - Database Seeding Script

Populates the database with comprehensive test data including:
- Teacher and student accounts
- Survey templates
- Active sessions with join tokens
- Sample submissions (both guest and authenticated)

#### Usage

```bash
# Seed database with sample data
uv run python scripts/seed.py
make db-seed
```

### `check_db_state.py` - Database State Checker

Simple script to check if the database is properly set up and contains data.

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
make db-status       # Show database record counts
make db-clean        # Clean all data (with confirmation)
make db-clean-force  # Force clean all data (no confirmation)
make db-seed         # Seed database with sample data
make db-check        # Check database state
make db-migrate      # Run database migrations
```

## Safety Features

### Confirmation Prompts
- The clean script always asks for confirmation before deleting data
- Use `--force` flag only in automated scripts where confirmation isn't possible

### Foreign Key Awareness
- Tables are cleared in the correct order to respect foreign key constraints
- No orphaned records or constraint violations

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

# 3. Re-seed with fresh data
make db-seed

# 4. Test your changes
make test
```

### Testing New Features

```bash
# Clean slate for testing
make db-clean-force
make db-seed

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
