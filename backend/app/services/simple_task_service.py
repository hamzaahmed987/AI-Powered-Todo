"""Business logic service for simplified task operations.

Mirrors the CLI's TodoCommands logic but adapted for FastAPI.
All validation happens here and in Pydantic schemas.
"""

from sqlalchemy.orm import Session
from app.models.simple_task import SimpleTask
from app.schemas.simple_task import TaskCreate, TaskUpdate


class TaskService:
    """Service layer for task operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_task(self, task_data: TaskCreate) -> SimpleTask:
        """Create a new task.

        Args:
            task_data: TaskCreate schema with description

        Returns:
            SimpleTask: The created task

        Raises:
            ValueError: If description is invalid
        """
        # Pydantic validation already happened in schema
        task = SimpleTask(description=task_data.description)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: int) -> SimpleTask | None:
        """Get a single task by ID.

        Args:
            task_id: The task ID

        Returns:
            SimpleTask or None if not found
        """
        return self.db.query(SimpleTask).filter(SimpleTask.id == task_id).first()

    def get_all_tasks(self) -> list[SimpleTask]:
        """Get all tasks in creation order.

        Returns:
            list: All tasks ordered by ID
        """
        return self.db.query(SimpleTask).order_by(SimpleTask.id).all()

    def update_task(self, task_id: int, task_data: TaskUpdate) -> SimpleTask | None:
        """Update a task's description.

        Args:
            task_id: The task ID
            task_data: TaskUpdate schema with new description

        Returns:
            SimpleTask or None if not found

        Raises:
            ValueError: If description is invalid
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.description = task_data.description
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_complete(self, task_id: int) -> SimpleTask | None:
        """Mark a task as complete.

        Args:
            task_id: The task ID

        Returns:
            SimpleTask or None if not found
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        task.completed = True
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID

        Returns:
            bool: True if deleted, False if not found
        """
        task = self.get_task(task_id)
        if task is None:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def get_stats(self) -> dict:
        """Get task statistics.

        Returns:
            dict: Total, completed, and pending counts
        """
        tasks = self.get_all_tasks()
        completed = sum(1 for t in tasks if t.completed)
        pending = len(tasks) - completed

        return {
            "total": len(tasks),
            "completed": completed,
            "pending": pending
        }
