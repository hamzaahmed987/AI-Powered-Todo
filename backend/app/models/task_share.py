"""Task sharing model for collaboration features.

Represents permission grants for task sharing between users.
This is used for P3 (Phase 3) collaboration features.
"""

from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime, timezone
from .base import Base, TimestampMixin, UUIDMixin


class ShareRole(str, Enum):
    """Enumeration of possible share roles."""
    VIEWER = "viewer"
    EDITOR = "editor"


class TaskShare(Base, UUIDMixin, TimestampMixin):
    """Model representing a shared task grant.

    Attributes:
        id: Unique identifier (UUID)
        task_id: UUID of shared task (FK to Task)
        user_id: UUID of user receiving share (FK to User)
        role: Permission level (viewer, editor)
        created_by: UUID of user who created the share (FK to User)
        shared_at: Timestamp when share was granted
    """

    __tablename__ = "task_shares"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(ShareRole), default=ShareRole.VIEWER, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    task = relationship(
        "Task",
        back_populates="task_shares",
        foreign_keys=[task_id],
    )
    user = relationship(
        "User",
        back_populates="task_shares",
        foreign_keys=[user_id],
    )
    shared_by = relationship(
        "User",
        back_populates="shared_tasks",
        foreign_keys=[created_by],
    )

    # Indexes
    __table_args__ = (
        Index("idx_task_share_task_id", "task_id"),
        Index("idx_task_share_user_id", "user_id"),
        Index("idx_task_share_created_by", "created_by"),
        Index("idx_task_share_task_user", "task_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<TaskShare(id={self.id}, task_id={self.task_id}, user_id={self.user_id}, role={self.role})>"

    def is_viewer_only(self) -> bool:
        """Check if share grants only view access.

        Returns:
            bool: True if role is viewer
        """
        return self.role == ShareRole.VIEWER

    def can_edit(self) -> bool:
        """Check if share grants edit access.

        Returns:
            bool: True if role is editor
        """
        return self.role == ShareRole.EDITOR
