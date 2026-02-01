"""Task-related Pydantic schemas.

Schemas for task creation, updates, and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.task import TaskStatus, TaskPriority, RecurrencePattern


class TaskCreate(BaseModel):
    """Task creation request schema.

    Attributes:
        title: Task title (required)
        description: Task description (optional)
        deadline: Task deadline (optional)
        priority: Task priority (optional)
        estimated_duration: Estimated duration in minutes (optional)
        tags: List of tags/labels (optional)
        category: Task category (optional)
        is_recurring: Whether task repeats (optional)
        recurrence_pattern: Recurrence frequency (optional)
        recurrence_end_date: When recurrence ends (optional)
        reminder_enabled: Enable reminder (optional)
        reminder_time: When to send reminder (optional)
    """
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=1440)
    tags: Optional[str] = Field(None, max_length=500)  # Comma-separated tags
    category: Optional[str] = Field(None, max_length=100)
    is_recurring: bool = False
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    recurrence_end_date: Optional[datetime] = None
    reminder_enabled: bool = False
    reminder_time: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Task update request schema.

    All fields are optional for partial updates.

    Attributes:
        title: Updated task title
        description: Updated task description
        status: Updated task status
        priority: Updated task priority
        deadline: Updated deadline
        estimated_duration: Updated estimated hours
        tags: Updated tags list
        category: Updated category
        is_recurring: Updated recurring flag
        recurrence_pattern: Updated recurrence pattern
        recurrence_end_date: Updated recurrence end date
        reminder_enabled: Updated reminder flag
        reminder_time: Updated reminder time
    """
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=999)
    tags: Optional[list[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_end_date: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Task response schema.

    Attributes:
        id: Task UUID
        title: Task title
        description: Task description
        status: Current task status
        priority: Task priority
        deadline: Task deadline
        estimated_duration: Estimated hours to complete
        completed_at: Timestamp when completed (null if not completed)
        ai_priority: AI-generated priority suggestion
        ai_estimated_duration: AI-generated duration estimate (hours)
        owner_id: UUID of task owner
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
        tags: List of task tags
        category: Task category
        is_recurring: Whether task is recurring
        recurrence_pattern: Recurrence frequency
        recurrence_end_date: When recurrence ends
        reminder_enabled: Whether reminder is enabled
        reminder_time: When reminder will be sent
    """
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    deadline: Optional[datetime]
    estimated_duration: Optional[int]
    completed_at: Optional[datetime]
    ai_priority: Optional[TaskPriority]
    ai_estimated_duration: Optional[int]
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    tags: Optional[str] = None  # Comma-separated tags
    category: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    recurrence_end_date: Optional[datetime] = None
    reminder_enabled: bool = False
    reminder_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskInDB(TaskResponse):
    """Task database schema (internal use).

    Extends TaskResponse with additional database fields if needed.
    """
    pass

    class Config:
        from_attributes = True


class TaskListParams(BaseModel):
    """Task list query parameters.

    Attributes:
        status: Filter by task status
        priority: Filter by task priority
        skip: Number of items to skip
        limit: Number of items to return
        category: Filter by category
        tags: Filter by tags
        is_recurring: Filter recurring tasks
        search: Search in title/description
    """
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    category: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated
    is_recurring: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=200)
