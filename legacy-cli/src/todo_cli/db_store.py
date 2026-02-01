"""Database-backed Task Storage Layer using SQLAlchemy and SQLite.

This module provides DatabaseTaskStore, which persists tasks to a SQLite database,
ensuring task IDs are assigned and managed by the database engine. This guarantees
that task numbering (01, 02, 03, etc.) is persistent and the single source of truth.

Design:
    - Uses SQLAlchemy ORM for database abstraction
    - SQLite for simple, file-based persistence
    - Compatible with existing TaskStore interface
    - Auto-incremented integer IDs assigned by database

Performance: All operations are O(1) or O(n) where n = task count
    - Add: O(1) - Single INSERT with auto-increment ID
    - Get: O(1) - Primary key lookup
    - Get All: O(n) - Sequential scan
    - Update: O(1) - Primary key update
    - Delete: O(1) - Primary key deletion
    - Mark Complete: O(1) - Primary key update

Classes:
    DatabaseTaskStore: SQLAlchemy-backed repository for persistent task management
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from .models import Task

# Get database path from environment or use default
DATA_DIR = os.getenv("TODO_DATA_DIR", os.path.expanduser("~/.todo_cli"))
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATA_DIR, "tasks.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Create declarative base for models
Base = declarative_base()


class TaskModel(Base):
    """SQLAlchemy model for persistent task storage.

    Attributes:
        id: Auto-incremented primary key (assigned by database)
        description: Task description (1-200 characters)
        completed: Task completion status (default: False)
        created_at: Timestamp when task was created (auto-set)
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    def to_task(self) -> Task:
        """Convert database model to Task domain object.

        Returns:
            Task: Domain object with database values
        """
        return Task(
            id=self.id,
            description=self.description,
            completed=self.completed,
            created_at=self.created_at,
        )


class DatabaseTaskStore:
    """SQLAlchemy-backed repository for persistent task storage.

    Uses SQLite database to ensure task IDs are persisted and managed by the
    database engine. This guarantees consistent, unique ID assignment across
    multiple runs of the application.

    Attributes:
        _session_factory: SQLAlchemy SessionLocal for database connections
    """

    def __init__(self) -> None:
        """Initialize DatabaseTaskStore and create tables if needed.

        Creates all required tables if they don't exist. Ready for CRUD
        operations immediately after initialization.
        """
        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Create session factory
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

    def _get_session(self) -> Session:
        """Create a new database session.

        Returns:
            Session: SQLAlchemy session for database operations
        """
        return self._session_factory()

    def add(self, description: str) -> Task:
        """Create and store a new task with database-assigned ID.

        Creates a Task object with the provided description. The database
        assigns the next sequential ID. Task validation happens in the
        Task model's __post_init__.

        Args:
            description (str): Task description (1-200 chars, non-empty required).
                Will be trimmed of whitespace and validated.

        Returns:
            Task: The newly created Task object with database-assigned ID.

        Raises:
            ValueError: If description fails Task validation.

        Performance:
            O(1) - Single database INSERT with auto-increment
        """
        session = self._get_session()
        try:
            # Validate description by creating a Task object
            # This ensures the same validation as before
            task = Task(id=0, description=description)  # Temp ID, will be replaced

            # Create database model
            db_task = TaskModel(
                description=task.description,
                completed=task.completed,
                created_at=task.created_at,
            )

            # Add to session and flush to get auto-assigned ID
            session.add(db_task)
            session.flush()  # Get the ID assigned by database

            # Create and return Task with database-assigned ID
            result = Task(
                id=db_task.id,
                description=db_task.description,
                completed=db_task.completed,
                created_at=db_task.created_at,
            )

            session.commit()
            return result
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID from database.

        Performs a primary key lookup to find the task with the specified ID.
        Returns None if the task does not exist.

        Args:
            task_id (int): ID of the task to retrieve.

        Returns:
            Optional[Task]: The Task object if found, None if not found.

        Performance:
            O(1) - Primary key lookup
        """
        session = self._get_session()
        try:
            db_task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if db_task:
                return db_task.to_task()
            return None
        finally:
            session.close()

    def get_all(self) -> list[Task]:
        """Retrieve all tasks from database in creation order.

        Returns a list of all Task objects, maintaining creation order by ID.
        The list is a copy, so modifying it won't affect storage, but
        modifying returned Task objects affects storage state.

        Returns:
            list[Task]: List of all Task objects, sorted by ID.
                Empty list if no tasks exist.

        Performance:
            O(n) - Iterate all tasks to build list (where n = task count)
        """
        session = self._get_session()
        try:
            db_tasks = (
                session.query(TaskModel).order_by(TaskModel.id).all()
            )
            return [task.to_task() for task in db_tasks]
        finally:
            session.close()

    def update(self, task_id: int, description: str) -> Task | None:
        """Update a task's description in the database.

        Finds the task by ID and updates its description while preserving
        other attributes. The new description is validated the same way
        as during task creation.

        Args:
            task_id (int): ID of the task to update.
            description (str): New task description (1-200 chars, non-empty).

        Returns:
            Optional[Task]: The updated Task object if found, None if not found.

        Raises:
            ValueError: If new description fails Task validation.

        Performance:
            O(1) - Primary key lookup and update
        """
        session = self._get_session()
        try:
            # Validate description using Task model
            task = Task(id=-1, description=description)

            # Update database
            db_task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if db_task is None:
                return None

            db_task.description = task.description
            session.commit()
            return db_task.to_task()
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    def delete(self, task_id: int) -> bool:
        """Delete a task from the database.

        Removes the task from storage permanently. The task ID is never reused.

        Args:
            task_id (int): ID of the task to delete.

        Returns:
            bool: True if task was found and deleted, False if not found.

        Performance:
            O(1) - Primary key deletion
        """
        session = self._get_session()
        try:
            db_task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if db_task is None:
                return False

            session.delete(db_task)
            session.commit()
            return True
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    def mark_complete(self, task_id: int) -> Task | None:
        """Mark a task as complete in the database.

        Sets a task's completed status to True. This operation is idempotent:
        calling mark_complete on an already-complete task has no effect.

        Args:
            task_id (int): ID of the task to mark as complete.

        Returns:
            Optional[Task]: The Task object with completed=True if found,
                None if not found.

        Performance:
            O(1) - Primary key lookup and update
        """
        session = self._get_session()
        try:
            db_task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if db_task is None:
                return None

            db_task.completed = True
            session.commit()
            return db_task.to_task()
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()
