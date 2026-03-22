"""
Database configuration and session management.

Uses SQLModel with SQLite (async-compatible via aiosqlite).
"""

from sqlmodel import SQLModel, Session, create_engine

from jobscraper.config import settings

# Create database engine
# For SQLite, we disable check_same_thread for async compatibility
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
)


def init_db() -> None:
    """Initialize database tables."""
    # Import models to ensure they're registered
    from jobscraper import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get a database session."""
    return Session(engine)


def drop_all_tables() -> None:
    """Drop all tables (use with caution)."""
    SQLModel.metadata.drop_all(engine)
