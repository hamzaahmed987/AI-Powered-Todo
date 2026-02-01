"""Simplified task management API endpoints for todo operations.

Routes for CRUD operations on tasks matching the original CLI functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.simple_task import SimpleTask
from app.schemas.simple_task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskDetailResponse,
    MessageResponse
)
from app.services.simple_task_service import TaskService


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependency to get task service."""
    return TaskService(db)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """Create a new task.

    **Request Body:**
    - `description`: Task description (1-200 chars, required)

    **Returns:**
    - `id`: Auto-assigned task ID
    - `description`: The task description
    - `completed`: False by default
    - `created_at`: ISO 8601 timestamp
    """
    task = service.create_task(task_data)
    return task


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List all tasks",
)
async def list_tasks(
    service: TaskService = Depends(get_task_service),
):
    """Get all tasks with statistics.

    **Returns:**
    - `tasks`: List of all tasks
    - `total`: Total number of tasks
    - `completed`: Number of completed tasks
    - `pending`: Number of pending tasks
    """
    tasks = service.get_all_tasks()
    stats = service.get_stats()

    return TaskListResponse(
        tasks=tasks,
        **stats
    )


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get a single task",
)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Get a single task by ID.

    **Path Parameters:**
    - `task_id`: The task ID

    **Returns:**
    - Task details or 404 if not found
    """
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return TaskDetailResponse(task=task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Update a task's description.

    **Path Parameters:**
    - `task_id`: The task ID

    **Request Body:**
    - `description`: New task description (1-200 chars)

    **Returns:**
    - Updated task or 404 if not found
    """
    task = service.update_task(task_id, task_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark task as complete",
)
async def complete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Mark a task as complete.

    **Path Parameters:**
    - `task_id`: The task ID

    **Returns:**
    - Updated task with completed=true or 404 if not found
    """
    task = service.mark_complete(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="Delete a task",
)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    """Delete a task by ID.

    **Path Parameters:**
    - `task_id`: The task ID

    **Returns:**
    - Success message or 404 if not found
    """
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return MessageResponse(
        message=f"Task {task_id} deleted successfully",
        success=True
    )
