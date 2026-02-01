"""User service for user management operations.

Handles user creation, retrieval, and validation.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.exceptions import ConflictError, NotFoundError
from app.services.auth_service import hash_password


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str | None = None,
) -> User:
    """Create a new user account.

    Args:
        db: Database session
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        full_name: User's display name (optional)

    Returns:
        User: Created user object

    Raises:
        ConflictError: If email already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise ConflictError(message=f"User with email {email} already exists")

    # Create new user
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve user by email address.

    Args:
        db: Database session
        email: User email to search for

    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Retrieve user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user_id: str,
    **kwargs,
) -> User:
    """Update user information.

    Args:
        db: Database session
        user_id: User UUID
        **kwargs: Fields to update (full_name, email, etc.)

    Returns:
        Updated User object

    Raises:
        NotFoundError: If user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError(resource="User")

    for key, value in kwargs.items():
        if hasattr(user, key) and key != "password_hash":
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def deactivate_user(db: Session, user_id: str) -> User:
    """Deactivate a user account.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Updated User object with is_active=False

    Raises:
        NotFoundError: If user not found
    """
    return update_user(db, user_id, is_active=False)
