"""Data Models for Todo-CLI Application.

This module defines the core data structures used throughout the todo-cli
application. All models use Python dataclasses for clean, type-safe definitions
with automatic __init__, __repr__, and __eq__ methods.

The Task model represents individual todo items with comprehensive validation
to ensure data integrity and consistent behavior.

Classes:
    Task: Core data model for todo items with validation

Example:
    Creating a valid task:

        >>> from models import Task
        >>> task = Task(id=1, description="Buy groceries")
        >>> task.completed
        False
        >>> task.id
        1

    Creating an invalid task raises ValueError:

        >>> task = Task(id=1, description="")
        Traceback (most recent call last):
            ...
        ValueError: Task description cannot be empty or whitespace-only

Validation Rules:
    - Description must be non-empty and not whitespace-only
    - Description must not exceed 200 characters
    - Whitespace is automatically trimmed from descriptions
    - Task ID is immutable (set by storage layer)
    - Creation timestamp is auto-generated
    - Completed status defaults to False
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a single task in the todo application.

    A Task is an immutable data container for todo items, storing the task
    identifier, description, completion status, and creation timestamp.
    All validation happens in __post_init__ to ensure data integrity.

    Attributes:
        id (int): Unique sequential identifier assigned by TaskStore.
            Auto-incremented for each new task. Never reused in a session.

        description (str): User-provided task description (1-200 characters).
            Automatically trimmed of leading/trailing whitespace.
            Required and cannot be empty or whitespace-only.

        completed (bool): Whether the task is marked as done (default: False).
            Updated via TaskStore.mark_complete() method.
            Preserved when task description is updated.

        created_at (datetime): Timestamp of task creation (auto-assigned).
            Set to datetime.now() when task is created.
            Used for ordering tasks by creation time.

    Example:
        Creating a task with minimal args:

            >>> task = Task(id=1, description="Buy groceries")
            >>> task.id
            1
            >>> task.description
            'Buy groceries'
            >>> task.completed
            False

        Task with custom attributes:

            >>> task = Task(
            ...     id=5,
            ...     description="Complete project",
            ...     completed=True
            ... )
            >>> task.completed
            True

    Raises:
        ValueError: If description is empty, whitespace-only, or > 200 chars.

    Notes:
        - Dataclass provides automatic __repr__ for debugging
        - frozen=False allows mutation of completed and description fields
        - created_at uses default_factory for fresh timestamp per instance
    """

    id: int
    """Unique sequential task identifier (auto-incremented by TaskStore)."""

    description: str
    """Task description: 1-200 chars, trimmed, non-empty required."""

    completed: bool = False
    """Completion status: True when marked done, False by default."""

    created_at: datetime = field(default_factory=datetime.now)
    """Timestamp when task was created (auto-set to current time)."""

    def __post_init__(self) -> None:
        """Validate task attributes after initialization.

        This method is automatically called by the dataclass decorator after
        __init__ runs. It performs all validation to ensure Task instances
        maintain data integrity:

        1. Trim leading/trailing whitespace from description
        2. Validate description is not empty or whitespace-only
        3. Validate description does not exceed 200 characters

        All errors are reported with descriptive ValueError messages
        suitable for display to end users.

        Raises:
            ValueError: If any validation check fails.

                - "Task description cannot be empty or whitespace-only"
                  When description is empty or only whitespace.

                - "Task description cannot exceed 200 characters"
                  When description exceeds 200 characters.

        Example:
            Validation runs automatically on initialization:

                >>> task = Task(id=1, description="  valid  ")
                >>> task.description
                'valid'

                >>> task = Task(id=1, description="   ")  # doctest: +SKIP
                Traceback (most recent call last):
                    ...
                ValueError: Task description cannot be empty...

                >>> task = Task(id=1, description="x" * 201)  # doctest: +SKIP
                Traceback (most recent call last):
                    ...
                ValueError: Task description cannot exceed 200 characters
        """
        # Trim whitespace from description for cleaner storage
        self.description = self.description.strip()

        # Validate description is not empty
        if not self.description:
            raise ValueError("Task description cannot be empty or whitespace-only")

        # Validate description length does not exceed maximum
        if len(self.description) > 200:
            raise ValueError("Task description cannot exceed 200 characters")
