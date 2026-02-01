"""Simplified Task model matching the original CLI structure.

Uses SQLAlchemy 2.0+ modern style with Mapped type hints and mapped_column.
Reference: https://docs.sqlalchemy.org/en/20/orm/declarative_tables
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models.

    Uses SQLAlchemy 2.0+ declarative base for modern ORM mapping.
    """
    pass


class SimpleTask(Base):
    """Simplified Task model - directly maps to CLI Task.

    Uses modern SQLAlchemy 2.0 style with Mapped type hints and mapped_column.
    This provides better type safety and IDE support compared to Column.

    Attributes:
        id: Sequential auto-increment ID (matches CLI behavior)
        description: Task description (1-200 chars, required, non-empty)
        completed: Boolean completion status (default: False)
        created_at: Timestamp when task was created (auto-set to current time)
    """

    __tablename__ = "simple_tasks"

    # Modern SQLAlchemy 2.0 style with Mapped and type hints
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Auto-incremented task ID"
    )
    description: Mapped[str] = mapped_column(
        comment="Task description (1-200 characters)"
    )
    completed: Mapped[bool] = mapped_column(
        default=False,
        comment="Task completion status"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        comment="Timestamp when task was created"
    )

    def __repr__(self) -> str:
        """Return string representation of task."""
        return f"<Task(id={self.id}, description={self.description[:50]}, completed={self.completed})>"

    def to_dict(self) -> dict:
        """Convert task to dictionary for API responses.

        Returns:
            dict: Task data with id, description, completed status, and created_at timestamp
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
