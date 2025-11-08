from __future__ import annotations

from typing import Dict

from sqlalchemy import MetaData, func, select
from sqlalchemy.orm import Session


def clear_database_data(db: Session) -> Dict[str, int]:
    """Remove all rows from every table while keeping schema intact.

    Returns a mapping of table name -> number of deleted rows.
    """

    metadata = MetaData()
    metadata.reflect(bind=db.bind)

    deleted_counts: Dict[str, int] = {}

    with db.begin():
        for table in reversed(metadata.sorted_tables):
            if table.name == "alembic_version":
                deleted_counts[table.name] = 0
                continue
            count = db.execute(select(func.count()).select_from(table)).scalar() or 0
            if count:
                db.execute(table.delete())
            deleted_counts[table.name] = int(count)

    return deleted_counts
