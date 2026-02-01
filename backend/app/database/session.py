"""Database session configuration and setup.

Provides SQLAlchemy engine, session factory, and Base class for ORM models.
Includes connection pooling optimized for Neon Serverless PostgreSQL.

Neon Connection String Format:
    postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require

The ?sslmode=require parameter is required for Neon connections.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from typing import Generator
from app.models.base import Base

# Database URL from environment or default
# Neon connection string should include ?sslmode=require parameter
_db_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_app?sslmode=require"
)
# Convert to psycopg3 driver format
DATABASE_URL = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Debug: Show which database we're connecting to (hide password)
_display_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
print(f"[DB] Connecting to: ...@{_display_url}")

# Create SQLAlchemy engine optimized for Neon Serverless PostgreSQL
# Serverless databases handle pooling on their side, so we use smaller pools
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # Essential: verify connections before using
    pool_size=3,              # Small pool for serverless
    max_overflow=5,
    pool_timeout=30,          # Wait up to 30s for connection (NeonDB cold start)
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries if enabled
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator:
    """Dependency injection for database session in FastAPI endpoints.

    Yields:
        Session: SQLAlchemy session object

    Example:
        @app.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            return db.query(Task).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables defined in models.

    This should be called once on application startup or during migration setup.
    For production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection():
    """Check if database connection is available.

    Returns:
        bool: True if connection successful, False otherwise
    """
    import concurrent.futures

    def _check():
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True

    try:
        # Use thread-based timeout (works on Windows and Unix)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_check)
            result = future.result(timeout=10)  # 10 second timeout
            return result
    except concurrent.futures.TimeoutError:
        print("Database connection check timed out after 10 seconds")
        return False
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
