# Database Migration Guide

## ⚠️ Critical: Survey Table Naming

**IMPORTANT**: This project uses the `surveys` table (NOT `survey_templates`).

### Current State ✅
- **Table**: `surveys` 
- **Model**: `SurveyTemplate` (maps to `surveys` table)
- **Foreign Key**: `sessions.survey_template_id` → `surveys.id`
- **API**: All endpoints use `surveys` table

### Historical Context
During development, the table was renamed from `survey_templates` to `surveys` for clarity. The old `survey_templates` table no longer exists.

## Quick Health Check

```bash
# Check database state
make db-check

# Or manually
uv run python scripts/check_db_state.py
```

## Migration Best Practices

### 1. Always Use Alembic
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migration
uv run alembic upgrade head

# Check status
uv run alembic current
```

### 2. Before Any Changes
```bash
# Verify current state
make db-check

# Check what tables exist
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name;'))
print('Tables:', [row[0] for row in result])
"
```

### 3. Common Scenarios

**Adding a Column to Surveys:**
```python
# In migration file
op.add_column("surveys", sa.Column("new_field", sa.String(255), nullable=True))
```

**Modifying Survey Schema:**
```python
# Always target 'surveys' table
op.alter_column("surveys", "existing_column", nullable=False)
```

**Adding Foreign Key to Surveys:**
```python
# Reference surveys table
op.create_foreign_key("fk_name", "other_table", "surveys", ["survey_id"], ["id"])
```

### 4. Emergency Recovery

If you accidentally create a `survey_templates` table:

```bash
# Check for both tables
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' AND table_name IN (\\'surveys\\', \\'survey_templates\\');'))
tables = [row[0] for row in result]
print('Found tables:', tables)
"

# If both exist, migrate and clean up
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
try:
    # Copy data if needed
    db.execute(text('INSERT INTO surveys SELECT * FROM survey_templates WHERE NOT EXISTS (SELECT 1 FROM surveys WHERE surveys.id = survey_templates.id);'))
    # Drop old table
    db.execute(text('DROP TABLE survey_templates;'))
    db.commit()
    print('✅ Migration completed')
except Exception as e:
    print('❌ Error:', e)
    db.rollback()
"
```

## Verification Checklist

After any migration:

- [ ] Run `make db-check`
- [ ] Verify `surveys` table exists
- [ ] Verify `survey_templates` table does NOT exist
- [ ] Check foreign keys point to `surveys.id`
- [ ] Test API endpoints work
- [ ] Check data integrity

## Schema Reference

**Current Tables:**
- `teachers` - Teacher accounts
- `courses` - Teacher courses
- `surveys` - Global survey templates ⚠️ (NOT survey_templates)
- `sessions` - Class sessions (references surveys.id)
- `submissions` - Student responses with scores

**Key Relationships:**
- `sessions.survey_template_id` → `surveys.id`
- `submissions.session_id` → `sessions.id`

## Troubleshooting

### Problem: "relation 'surveys' does not exist"
**Solution**: Run `uv run alembic upgrade head`

### Problem: "relation 'survey_templates' does not exist" 
**Solution**: This is correct! The table was renamed to `surveys`

### Problem: Both tables exist
**Solution**: Run the emergency recovery script above

### Problem: Foreign key errors
**Solution**: Check that foreign keys point to `surveys.id`, not `survey_templates.id`

## Remember

- ✅ Use `surveys` table for all survey operations
- ✅ Never create `survey_templates` table
- ✅ Always run `make db-check` before making changes
- ✅ Use Alembic for all schema changes
- ✅ Test API endpoints after migrations
