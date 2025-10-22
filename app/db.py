from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create database engine - use PostgreSQL for development
engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
