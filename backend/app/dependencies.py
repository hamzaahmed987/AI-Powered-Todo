"""FastAPI dependency injection utilities.

Provides reusable dependencies for database sessions and authentication.
"""

from typing import Generator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, get_db
from app.models.user import User
from app.services.auth_service import verify_token
from app.utils.exceptions import UnauthorizedError, NotFoundError

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Dependency for database session.

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Dependency for authenticated endpoints.

    Verifies JWT token from Authorization header and returns current user object.

    Args:
        request: HTTP request containing Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Example:
        @app.get("/me")
        def get_profile(user: User = Depends(get_current_user)):
            return user
    """
    # Extract bearer token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Verify token and get user ID
    user_id_str = verify_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert user_id string to UUID for database query
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    # Note: expire_on_commit=False ensures we can access user data even after session closes
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Log for debugging
        from app.utils.logger import logger
        logger.warning(f"User not found in database: user_id={user_id}, user_id_type={type(user_id)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Dependency for endpoints that may have optional authentication.

    Returns current user if authenticated, None otherwise.

    Args:
        request: HTTP request containing optional Authorization header
        db: Database session

    Returns:
        Optional[User]: User object if authenticated, None otherwise

    Example:
        @app.get("/tasks")
        def list_tasks(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return f"Tasks for {user.email}"
            else:
                return "Public tasks"
    """
    # Extract bearer token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Verify token and get user ID
    user_id_str = verify_token(token)
    if not user_id_str:
        return None

    # Convert user_id string to UUID for database query
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        return None

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    return user
