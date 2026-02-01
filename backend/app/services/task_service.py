"""Task service for task management operations.

Handles task CRUD, filtering, and access control.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
import time

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_share import TaskShare, ShareRole
from app.utils.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.utils.logger import log_database_operation
from app.utils.cache import cached, invalidate_cache


def create_task(
    db: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
    deadline: Optional[datetime] = None,
    estimated_duration: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
) -> Task:
    """Create a new task for a user.

    Args:
        db: Database session
        user_id: UUID of task owner
        title: Task title (required)
        description: Task description (optional)
        deadline: Task deadline (optional)
        estimated_duration: Estimated duration in minutes (optional)
        priority: Task priority (optional, defaults to MEDIUM)

    Returns:
        Created Task object
    """
    start_time = time.time()

    # Validate inputs
    if not title or len(title.strip()) == 0:
        raise ValidationError("Task title is required and cannot be empty")

    if len(title.strip()) > 500:
        raise ValidationError("Task title must not exceed 500 characters")

    if description and len(description) > 5000:
        raise ValidationError("Task description must not exceed 5000 characters")

    if estimated_duration is not None and (estimated_duration < 1 or estimated_duration > 1440):
        raise ValidationError("Estimated duration must be between 1 and 1440 minutes (24 hours)")

    task = Task(
        owner_id=user_id,
        title=title.strip(),
        description=description,
        deadline=deadline,
        estimated_duration=estimated_duration,
        priority=priority or TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    duration = time.time() - start_time
    log_database_operation(
        operation="INSERT",
        table="tasks",
        duration=duration,
        records_affected=1
    )

    return task


def get_task(
    db: Session,
    task_id: UUID,
    user_id: UUID,
) -> Task:
    """Retrieve a single task if user has access.

    Args:
        db: Database session
        task_id: Task UUID
        user_id: User UUID requesting access

    Returns:
        Task object

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If user doesn't have access to task
    """
    start_time = time.time()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise NotFoundError(resource="Task")

    # Check if user has access (owns task or has share)
    if not can_access_task(db, task_id, user_id):
        raise ForbiddenError(message="You do not have access to this task")

    duration = time.time() - start_time
    log_database_operation(
        operation="SELECT",
        table="tasks",
        duration=duration,
        records_affected=1
    )

    return task


def get_user_tasks(
    db: Session,
    user_id: UUID,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[list[Task], int]:
    """Get all tasks for a user with optional filtering.

    Args:
        db: Database session
        user_id: User UUID
        status: Filter by task status (optional)
        priority: Filter by task priority (optional)
        skip: Number of items to skip for pagination
        limit: Number of items to return

    Returns:
        Tuple of (tasks list, total count)
    """
    start_time = time.time()

    # Use a single query for both count and results to avoid double query
    query = db.query(Task).filter(Task.owner_id == user_id)

    # Apply status filter
    if status:
        query = query.filter(Task.status == status)

    # Apply priority filter
    if priority:
        query = query.filter(Task.priority == priority)

    # Count total records with the same filters (but without offset/limit)
    total_start = time.time()
    total = query.count()
    total_duration = time.time() - total_start

    # Apply pagination and ordering
    tasks_start = time.time()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    tasks_duration = time.time() - tasks_start

    duration = time.time() - start_time
    log_database_operation(
        operation="SELECT",
        table="tasks",
        duration=duration,
        records_affected=len(tasks)
    )

    return tasks, total


def update_task(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    **kwargs,
) -> Task:
    """Update a task if user owns it.

    Args:
        db: Database session
        task_id: Task UUID
        user_id: User UUID requesting update
        **kwargs: Fields to update (title, status, priority, etc.)

    Returns:
        Updated Task object

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If user doesn't own the task
        ValidationError: If validation fails
    """
    start_time = time.time()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise NotFoundError(resource="Task")

    # Verify ownership
    if task.owner_id != user_id:
        raise ForbiddenError(message="You do not have permission to update this task")

    # Validate inputs before updating
    title = kwargs.get('title')
    description = kwargs.get('description')
    estimated_duration = kwargs.get('estimated_duration')

    if title is not None:
        title = title.strip()
        if not title:
            raise ValidationError("Task title cannot be empty")
        if len(title) > 500:
            raise ValidationError("Task title must not exceed 500 characters")
        kwargs['title'] = title

    if description is not None and len(description) > 5000:
        raise ValidationError("Task description must not exceed 5000 characters")

    if estimated_duration is not None and (estimated_duration < 1 or estimated_duration > 1440):
        raise ValidationError("Estimated duration must be between 1 and 1440 minutes (24 hours)")

    # Update allowed fields
    allowed_fields = {
        "title",
        "description",
        "status",
        "priority",
        "deadline",
        "estimated_duration",
        "ai_priority",
        "ai_estimated_duration",
        "completed_at",
    }

    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            setattr(task, key, value)

    # If status is set to COMPLETED, set completed_at
    if "status" in kwargs and kwargs["status"] == TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)

    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    duration = time.time() - start_time
    log_database_operation(
        operation="UPDATE",
        table="tasks",
        duration=duration,
        records_affected=1
    )

    return task


def delete_task(
    db: Session,
    task_id: UUID,
    user_id: UUID,
) -> None:
    """Delete a task if user owns it.

    Args:
        db: Database session
        task_id: Task UUID
        user_id: User UUID requesting deletion

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If user doesn't own the task
    """
    start_time = time.time()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise NotFoundError(resource="Task")

    # Verify ownership
    if task.owner_id != user_id:
        raise ForbiddenError(message="You do not have permission to delete this task")

    db.delete(task)
    db.commit()

    duration = time.time() - start_time
    log_database_operation(
        operation="DELETE",
        table="tasks",
        duration=duration,
        records_affected=1
    )


def can_access_task(
    db: Session,
    task_id: UUID,
    user_id: UUID,
) -> bool:
    """Check if user can access a task (owns it or has share).

    Args:
        db: Database session
        task_id: Task UUID
        user_id: User UUID

    Returns:
        True if user has access, False otherwise
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return False

    # User owns the task
    if task.owner_id == user_id:
        return True

    # User has a share for the task
    share = (
        db.query(TaskShare)
        .filter(TaskShare.task_id == task_id, TaskShare.user_id == user_id)
        .first()
    )

    return share is not None


def update_ai_suggestions(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    priority: Optional[TaskPriority] = None,
    estimated_duration: Optional[int] = None,
) -> Task:
    """Update AI-generated suggestions for a task.

    Args:
        db: Database session
        task_id: Task UUID
        user_id: User UUID (must own task)
        priority: AI-generated priority
        estimated_duration: AI-generated duration estimate (hours)

    Returns:
        Updated Task object

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If user doesn't own the task
    """
    return update_task(
        db,
        task_id,
        user_id,
        ai_priority=priority,
        ai_estimated_duration=estimated_duration,
    )
