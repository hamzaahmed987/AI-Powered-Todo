"""Pydantic schemas for simple task validation and API responses."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task description (1-200 characters)"
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty after trimming."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task description cannot be empty or whitespace-only")
        if len(trimmed) > 200:
            raise ValueError("Task description cannot exceed 200 characters")
        return trimmed


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="New task description"
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task description cannot be empty or whitespace-only")
        if len(trimmed) > 200:
            raise ValueError("Task description cannot exceed 200 characters")
        return trimmed


class TaskResponse(BaseModel):
    """Schema for task response in API."""

    id: int
    description: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""

    tasks: list[TaskResponse]
    total: int
    completed: int
    pending: int


class TaskDetailResponse(BaseModel):
    """Schema for detailed task response."""

    task: TaskResponse


class MessageResponse(BaseModel):
    """Schema for simple message response."""

    message: str
    success: bool
