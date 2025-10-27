from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

# Global Base for all ORM models
Base = declarative_base()

# Create the database engine
# Using DATABASE_URL from environment (.env or Docker)
engine = create_engine(settings.database_url, echo=True)

# Session factory for FastAPI dependencies
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
