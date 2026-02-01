"""Simplified database session management for SQLite.

Uses SQLAlchemy ORM with SQLite for development/demo.
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os

# Database URL - uses SQLite file or in-memory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# Create engine with appropriate config for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """Get database session dependency.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables.

    Must be called before running the app.
    """
    from app.models.simple_task import Base
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """Check if database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            # Check SQLite version
            result = conn.execute("SELECT 1")
            result.close()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


def get_table_info(table_name: str) -> dict | None:
    """Get information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
        dict: Table information or None if table doesn't exist
    """
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return None

    return {
        "columns": inspector.get_columns(table_name),
        "primary_keys": inspector.get_pk_constraint(table_name),
        "indexes": inspector.get_indexes(table_name),
    }


def drop_all_tables():
    """Drop all tables from database.

    WARNING: This will delete all data!
    """
    from app.models.simple_task import Base
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    # Script to initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Tables: {inspect(engine).get_table_names()}")
