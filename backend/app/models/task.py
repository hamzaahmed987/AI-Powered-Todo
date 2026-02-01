"""Task model for todo management with AI enhancements.

Represents a task with status, priority, deadlines, and AI-generated suggestions.
"""

from enum import Enum
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from .base import Base, TimestampMixin, UUIDMixin


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Enumeration of possible task priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Enumeration of recurrence patterns for recurring tasks."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Task(Base, UUIDMixin, TimestampMixin):
    """Task model representing a todo item.

    Attributes:
        id: Unique identifier (UUID)
        owner_id: UUID of user who owns this task (FK to User)
        title: Task title (required)
        description: Detailed task description
        status: Current task status (pending, in_progress, completed)
        priority: Task priority level (low, medium, high, urgent)
        deadline: Optional deadline datetime
        estimated_duration: Estimated hours to complete task
        completed_at: Timestamp when task was completed
        ai_priority: AI-generated priority suggestion
        ai_estimated_duration: AI-generated duration estimate (hours)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
        owner: Relationship to User object
        task_shares: Relationship to TaskShare objects
    """

    __tablename__ = "tasks"

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in hours
    completed_at = Column(DateTime(timezone=True), nullable=True)
    ai_priority = Column(SQLEnum(TaskPriority), nullable=True)
    ai_estimated_duration = Column(Integer, nullable=True)  # in hours

    # Tags/Categories (stored as comma-separated string for compatibility)
    tags = Column(Text, default="", nullable=True)  # Comma-separated tags
    category = Column(String(100), nullable=True)

    # Recurring task fields
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(SQLEnum(RecurrencePattern), default=RecurrencePattern.NONE, nullable=False)
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    # Notification/Reminder fields
    reminder_enabled = Column(Boolean, default=False, nullable=False)
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="tasks", foreign_keys=[owner_id])
    task_shares = relationship(
        "TaskShare",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    # Self-referential relationship for recurring tasks
    parent_task = relationship("Task", remote_side="Task.id", backref="child_tasks")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_task_owner_id", "owner_id"),
        Index("idx_task_status", "status"),
        Index("idx_task_deadline", "deadline"),
        Index("idx_task_owner_status", "owner_id", "status"),
        Index("idx_task_created_at", "created_at"),
        Index("idx_task_category", "category"),
        Index("idx_task_is_recurring", "is_recurring"),
        Index("idx_task_reminder", "reminder_enabled", "reminder_time"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status}, owner_id={self.owner_id})>"

    def mark_completed(self):
        """Mark task as completed and set completed_at timestamp."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def is_overdue(self) -> bool:
        """Check if task is overdue.

        Returns:
            bool: True if deadline is in the past and task is not completed
        """
        if not self.deadline or self.status == TaskStatus.COMPLETED:
            return False
        return self.deadline < datetime.now(timezone.utc)

    def time_until_deadline(self) -> timedelta | None:
        """Calculate time remaining until deadline.

        Returns:
            timedelta: Time remaining, or None if no deadline or completed
        """
        if not self.deadline or self.status == TaskStatus.COMPLETED:
            return None
        return self.deadline - datetime.now(timezone.utc)
