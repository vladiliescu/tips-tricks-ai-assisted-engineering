from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

from app.core.config import settings

# Create SQLAlchemy engine
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.database_echo,
    )
else:
    engine = create_engine(settings.database_url, echo=settings.database_echo)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Metadata instance for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """
    Initialize the database.
    Creates all tables defined in models.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import github, team, prediction

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_database_session() -> Session:
    """
    Get a database session for non-dependency injection use cases.
    Remember to close the session when done.
    """
    return SessionLocal()


def close_db_connection():
    """
    Close database connection.
    Useful for cleanup in tests or shutdown procedures.
    """
    engine.dispose()
