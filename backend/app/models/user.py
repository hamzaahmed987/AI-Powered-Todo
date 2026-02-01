"""User model for authentication and authorization.

Represents a user account in the application with password-based authentication.
"""

from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from .base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User account model.

    Attributes:
        id: Unique identifier (UUID)
        email: User email address (unique, case-insensitive)
        password_hash: Bcrypt hashed password
        full_name: User's display name
        is_active: Whether account is active
        created_at: Account creation timestamp
        updated_at: Last account modification timestamp
        tasks: Relationship to Task objects owned by user
        task_shares: Relationship to TaskShare objects (tasks shared with this user)
        shared_tasks: Relationship to TaskShare objects (tasks shared by this user)
    """

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tasks = relationship(
        "Task",
        back_populates="owner",
        foreign_keys="Task.owner_id",
        cascade="all, delete-orphan",
    )
    task_shares = relationship(
        "TaskShare",
        back_populates="user",
        foreign_keys="TaskShare.user_id",
        cascade="all, delete-orphan",
    )
    shared_tasks = relationship(
        "TaskShare",
        back_populates="shared_by",
        foreign_keys="TaskShare.created_by",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash.

        This method should be called from auth_service.verify_password()
        to maintain password verification logic in one place.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches hash, False otherwise
        """
        from app.services.auth_service import verify_password as verify_pwd
        return verify_pwd(password, self.password_hash)
