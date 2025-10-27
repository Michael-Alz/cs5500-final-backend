"""
alembic/env.py
Configured to work with app.models.Base and app.core.config.settings.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import app settings and Base
from app.core.config import settings
from app.db import Base

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use our app's metadata for autogenerate support
target_metadata = Base.metadata


def get_url():
    """Return the database URL from app settings (instead of alembic.ini)."""
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # detect column type changes
        compare_server_default=True,  # detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with DB connection)."""
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Choose online/offline based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
