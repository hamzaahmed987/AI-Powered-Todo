"""Business Logic Layer for Todo-CLI Application.

This module implements the command layer that sits between the CLI interface
and the storage layer, providing business logic, validation, and orchestration
for all todo operations. It transforms user requests into storage operations
and prepares responses suitable for display.

The command layer follows the Command Pattern, encapsulating each operation
as a method that returns a standardized CommandResult containing success status,
user-facing messages, and optional data payloads.

Architecture:
    CLI Layer (cli.py)
        ↓ Parses user input into command + arguments
    Command Layer (commands.py) ← YOU ARE HERE
        ↓ Validates, orchestrates business logic
    Storage Layer (store.py)
        ↓ Performs CRUD operations
    Data Model (models.py)

Responsibilities:
    - Input validation and normalization
    - Business rule enforcement
    - Error message formatting
    - Success/failure result packaging
    - Storage layer orchestration

Key Design Principles:
    1. Single Responsibility: Each command method handles one user operation
    2. Separation of Concerns: Commands don't know about CLI presentation
    3. Fail Fast: Validate inputs early and return clear error messages
    4. Consistent Responses: All operations return CommandResult objects
    5. Stateless Operations: Commands don't maintain operation state

Classes:
    CommandResult: Standardized result container for command operations
    TodoCommands: Main business logic coordinator for all todo operations

Example:
    Basic usage with TaskStore:

        >>> from store import TaskStore
        >>> from commands import TodoCommands
        >>> store = TaskStore()
        >>> commands = TodoCommands(store)
        >>> result = commands.add("Buy groceries")
        >>> result.success
        True
        >>> result.message
        'Task added successfully (ID: 1)'
        >>> result.data.description
        'Buy groceries'

    Error handling:

        >>> result = commands.add("")
        >>> result.success
        False
        >>> result.message
        'Error: Task description cannot be empty or whitespace-only'
        >>> result.data is None
        True

Performance Characteristics:
    All operations are O(1) or O(n) where n = task count:
    - add(): O(1) - Single store insertion
    - list_all(): O(n) - Retrieve and return all tasks
    - complete(): O(1) - Single task lookup and update
    - update(): O(1) - Single task lookup and mutation
    - delete(): O(1) - Single task lookup and removal

Error Handling Philosophy:
    - User errors return CommandResult(success=False, message=...)
    - System errors (programming bugs) raise exceptions
    - All error messages are user-friendly and actionable
    - Validation failures include hints about requirements

Thread Safety:
    This module is NOT thread-safe. It assumes single-threaded access
    matching the CLI REPL model. Concurrent operations would require
    locking around TaskStore operations.
"""

from dataclasses import dataclass
from typing import Any

from todo_cli.store import TaskStore


@dataclass
class CommandResult:
    """Standardized result container for command operations.

    CommandResult provides a consistent interface for returning operation
    results to the CLI layer. It encapsulates three pieces of information:
    1. Success/failure status (boolean)
    2. User-facing message (string)
    3. Optional data payload (any type)

    This pattern allows the CLI to handle all commands uniformly:
    - Check success to determine if operation completed
    - Display message to user (success confirmation or error)
    - Use data for further processing (e.g., displaying task details)

    The immutable dataclass design ensures results can't be accidentally
    modified after creation, preventing bugs from mutation.

    Attributes:
        success (bool): Whether the operation completed successfully.
            True = operation succeeded, result is valid
            False = operation failed, check message for details

        message (str): User-facing message describing the result.
            For success: Confirmation message (e.g., "Task added successfully")
            For failure: Error description with actionable guidance
            Always suitable for direct display to end users

        data (Any | None): Optional payload containing operation results.
            For queries: The requested data (Task, list[Task], etc.)
            For mutations: The modified object (updated Task, etc.)
            For failures: Typically None, but may contain partial data
            Default: None when no data needs to be returned

    Design Rationale:
        - Immutable dataclass prevents accidental mutation bugs
        - Typed fields enable static type checking
        - Optional data field allows flexibility for different operations
        - Separates success status from data presence (empty list vs error)

    Example:
        Success with data:

            >>> result = CommandResult(
            ...     success=True,
            ...     message="Task added successfully (ID: 1)",
            ...     data=Task(id=1, description="Buy milk")
            ... )
            >>> result.success
            True
            >>> result.data.id
            1

        Success without data:

            >>> result = CommandResult(
            ...     success=True,
            ...     message="Task deleted successfully",
            ...     data=None
            ... )
            >>> result.success
            True
            >>> result.data is None
            True

        Failure case:

            >>> result = CommandResult(
            ...     success=False,
            ...     message="Error: Task with ID 999 not found"
            ... )
            >>> result.success
            False
            >>> result.data is None
            True

    Notes:
        - frozen=False allows the dataclass to be mutable if needed
        - All fields have type hints for static analysis
        - data field accepts Any type for maximum flexibility
        - The pattern is inspired by Result/Either monads in functional programming
    """

    success: bool
    """Operation success status: True if completed, False if failed."""

    message: str
    """User-facing message: confirmation for success, error description for failure."""

    data: Any | None = None
    """Optional payload: query results, modified objects, or None for simple operations."""


class TodoCommands:
    """Business logic coordinator for todo application operations.

    TodoCommands acts as the service layer between the CLI and storage,
    implementing all business logic, validation, and error handling for
    todo operations. It orchestrates TaskStore operations and transforms
    low-level storage results into user-friendly CommandResult objects.

    Responsibilities:
        1. Input Validation: Check arguments before storage operations
        2. Business Logic: Enforce rules (e.g., detect already-complete tasks)
        3. Error Handling: Catch exceptions and return user-friendly messages
        4. Result Packaging: Convert storage results into CommandResult objects
        5. Message Formatting: Create consistent, actionable user messages

    Architecture Position:
        CLI → TodoCommands → TaskStore → Task
        TodoCommands knows about TaskStore and Task, but not about CLI

    Internal State:
        _store (TaskStore): The storage layer instance for task persistence.
            All CRUD operations are delegated to this store.
            Injected via constructor (dependency injection pattern).

    Attributes:
        _store: TaskStore instance for task operations

    Design Patterns:
        - Service Layer: Encapsulates business logic
        - Dependency Injection: TaskStore injected via constructor
        - Command Pattern: Each method is a discrete command
        - Result Object: Consistent CommandResult return type

    Example:
        Complete workflow:

            >>> from store import TaskStore
            >>> store = TaskStore()
            >>> commands = TodoCommands(store)
            >>> # Add task
            >>> result = commands.add("Write documentation")
            >>> result.success
            True
            >>> # List tasks
            >>> result = commands.list_all()
            >>> len(result.data)
            1
            >>> # Complete task
            >>> result = commands.complete(1)
            >>> result.success
            True
            >>> # Update task
            >>> result = commands.update(1, "Write comprehensive docs")
            >>> result.success
            True
            >>> # Delete task
            >>> result = commands.delete(1)
            >>> result.success
            True

    Notes:
        - All methods return CommandResult for consistent error handling
        - Private _store attribute prevents external manipulation
        - No global state - all operations go through injected store
        - Methods are stateless - no operation state persists between calls
    """

    def __init__(self, store: TaskStore) -> None:
        """Initialize TodoCommands with a TaskStore instance.

        Constructor uses dependency injection pattern, accepting a TaskStore
        instance that will be used for all storage operations. This design
        allows for easy testing (mock stores) and flexibility (different
        storage implementations).

        The store is saved as a private attribute (_store) to prevent
        external code from directly manipulating the storage layer,
        enforcing that all operations go through the command methods.

        Args:
            store (TaskStore): The storage layer instance to use for all
                task operations. Must be a valid TaskStore instance with
                full CRUD capabilities.

        Example:
            Basic initialization:

                >>> from store import TaskStore
                >>> store = TaskStore()
                >>> commands = TodoCommands(store)

            Using the same store for multiple operations:

                >>> store = TaskStore()
                >>> commands = TodoCommands(store)
                >>> commands.add("Task 1")
                >>> commands.add("Task 2")
                >>> result = commands.list_all()
                >>> len(result.data)
                2

        Notes:
            - Store is saved as _store (private) to prevent external access
            - No validation on store parameter - assumes valid TaskStore
            - Store is not copied - same instance used throughout lifetime
        """
        self._store: TaskStore = store

    def add(self, description: str) -> CommandResult:
        """Create a new task with the provided description.

        Validates the description and creates a new task in storage with an
        auto-assigned ID. Returns success with task details or failure with
        a user-friendly error message explaining validation failures.

        Validation Rules:
            1. Description cannot be empty or whitespace-only
            2. Description cannot exceed 200 characters
            3. Description is automatically trimmed of whitespace

        The method delegates actual task creation to TaskStore.add(), which
        handles ID assignment and storage. Any validation errors from the
        Task model are caught and converted into user-friendly messages.

        Args:
            description (str): The task description text provided by the user.
                Will be trimmed and validated against Task model requirements.
                Can contain any characters including special characters.
                Length range: 1-200 characters after trimming.

        Returns:
            CommandResult: Result object with one of the following states:

                Success case:
                    success=True
                    message="Task added successfully (ID: {id})"
                    data=Task object (newly created task)

                Failure case (validation error):
                    success=False
                    message="Error: {validation_error}"
                    data=None

        Performance:
            O(1) - Single validation check and store insertion

        Example:
            Successful task creation:

                >>> commands = TodoCommands(TaskStore())
                >>> result = commands.add("Buy groceries")
                >>> result.success
                True
                >>> result.message
                'Task added successfully (ID: 1)'
                >>> result.data.description
                'Buy groceries'
                >>> result.data.completed
                False

            Empty description error:

                >>> result = commands.add("")
                >>> result.success
                False
                >>> result.message
                'Error: Task description cannot be empty or whitespace-only'
                >>> result.data is None
                True

            Whitespace-only description error:

                >>> result = commands.add("   ")
                >>> result.success
                False
                >>> "empty" in result.message.lower()
                True

            Description too long error:

                >>> long_desc = "x" * 201
                >>> result = commands.add(long_desc)
                >>> result.success
                False
                >>> "200 characters" in result.message
                True

            Whitespace trimming:

                >>> result = commands.add("  task with spaces  ")
                >>> result.success
                True
                >>> result.data.description
                'task with spaces'

        Error Handling:
            - ValueError from Task validation: Converted to CommandResult failure
            - User sees exact validation error from Task.__post_init__
            - No exception propagates to caller (all errors returned as results)

        Notes:
            - Description is trimmed by Task.__post_init__, not here
            - Task ID is auto-assigned by TaskStore, not passed in
            - created_at timestamp is auto-generated by Task
            - completed status defaults to False
            - No duplicate checking - same description allowed multiple times
        """
        try:
            # Delegate task creation to storage layer
            # TaskStore.add() will create Task, which validates in __post_init__
            task = self._store.add(description)

            # Success: Return confirmation with task ID and data
            return CommandResult(
                success=True,
                message=f"Task added successfully (ID: {task.id})",
                data=task
            )
        except ValueError as error:
            # Validation failed in Task.__post_init__
            # Convert exception to user-friendly error result
            return CommandResult(
                success=False,
                message=f"Error: {str(error)}",
                data=None
            )

    def list_all(self) -> CommandResult:
        """Retrieve all tasks from storage.

        Fetches all tasks and returns them in a CommandResult. If no tasks
        exist, returns a helpful message guiding users to add tasks. If tasks
        exist, returns them as a list for display by the CLI.

        The method always returns success=True because retrieving an empty
        list is not an error condition - it's valid state. The CLI layer
        uses the data field to determine what to display.

        Returns:
            CommandResult: Result object with one of the following states:

                No tasks case:
                    success=True
                    message="No tasks found. Add a task using 'add <description>'"
                    data=[] (empty list)

                Tasks exist case:
                    success=True
                    message="Found {count} task(s)"
                    data=list[Task] (all tasks in creation order)

        Performance:
            O(n) where n = number of tasks
            Must iterate all tasks to build list

        Example:
            Empty task list:

                >>> commands = TodoCommands(TaskStore())
                >>> result = commands.list_all()
                >>> result.success
                True
                >>> result.message
                "No tasks found. Add a task using 'add <description>'"
                >>> result.data
                []

            With tasks:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task 1")
                >>> commands.add("Task 2")
                >>> result = commands.list_all()
                >>> result.success
                True
                >>> result.message
                'Found 2 task(s)'
                >>> len(result.data)
                2
                >>> [t.description for t in result.data]
                ['Task 1', 'Task 2']

            Tasks in creation order:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("First")
                >>> commands.add("Second")
                >>> commands.add("Third")
                >>> result = commands.list_all()
                >>> [t.id for t in result.data]
                [1, 2, 3]

        Notes:
            - Always returns success=True (empty list is valid, not error)
            - Tasks are returned in creation order (sorted by ID ascending)
            - Returned list contains actual Task objects (not copies)
            - Modifying returned Task objects affects storage state
            - CLI layer is responsible for formatting display
        """
        # Retrieve all tasks from storage layer
        tasks = self._store.get_all()

        # Check if task list is empty
        if not tasks:
            # Return empty result with helpful guidance message
            return CommandResult(
                success=True,
                message="No tasks found. Add a task using 'add <description>'",
                data=[]
            )

        # Return tasks with count in message
        return CommandResult(
            success=True,
            message=f"Found {len(tasks)} task(s)",
            data=tasks
        )

    def complete(self, task_id: int) -> CommandResult:
        """Mark a task as completed.

        Attempts to mark the specified task as complete. Handles three cases:
        1. Task not found - returns error
        2. Task already complete - returns informational message
        3. Task incomplete - marks complete and returns success

        This method implements business logic for completion:
        - Validates task exists
        - Detects already-complete state (idempotency check)
        - Provides appropriate feedback for each case

        Args:
            task_id (int): The unique identifier of the task to complete.
                Must be a valid task ID that exists in storage.

        Returns:
            CommandResult: Result object with one of the following states:

                Task not found:
                    success=False
                    message="Error: Task with ID {id} not found"
                    data=None

                Already complete:
                    success=True
                    message="Task {id} is already complete"
                    data=Task object (unchanged)

                Successfully completed:
                    success=True
                    message="Task {id} marked as complete"
                    data=Task object (with completed=True)

        Performance:
            O(1) - Single task lookup and flag update

        Example:
            Complete an incomplete task:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task to complete")
                >>> result = commands.complete(1)
                >>> result.success
                True
                >>> result.message
                'Task 1 marked as complete'
                >>> result.data.completed
                True

            Task not found:

                >>> commands = TodoCommands(TaskStore())
                >>> result = commands.complete(999)
                >>> result.success
                False
                >>> result.message
                'Error: Task with ID 999 not found'

            Already complete (idempotent):

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task")
                >>> commands.complete(1)
                >>> result = commands.complete(1)
                >>> result.success
                True
                >>> result.message
                'Task 1 is already complete'

        Notes:
            - Returns success=True for already-complete (idempotent operation)
            - Task object is returned in data field for both success cases
            - Only returns success=False when task doesn't exist
            - Completion is permanent (no "uncomplete" operation)
            - No validation on task_id parameter (assumes valid integer)
        """
        # Look up task in storage
        task = self._store.get(task_id)

        # Case 1: Task not found
        if task is None:
            return CommandResult(
                success=False,
                message=f"Error: Task with ID {task_id} not found",
                data=None
            )

        # Case 2: Task already complete (idempotent check)
        if task.completed:
            return CommandResult(
                success=True,
                message=f"Task {task_id} is already complete",
                data=task
            )

        # Case 3: Mark task as complete
        completed_task = self._store.mark_complete(task_id)

        return CommandResult(
            success=True,
            message=f"Task {task_id} marked as complete",
            data=completed_task
        )

    def update(self, task_id: int, description: str) -> CommandResult:
        """Update a task's description.

        Changes the description of an existing task while preserving all other
        attributes (ID, completion status, creation timestamp). Validates both
        that the task exists and that the new description is valid.

        Business Rules:
            - Task must exist (error if not found)
            - New description must pass same validation as add()
            - Completion status is preserved
            - Creation timestamp unchanged
            - Task ID never changes

        Args:
            task_id (int): The unique identifier of the task to update.
                Must be a valid task ID that exists in storage.

            description (str): The new description text to replace current one.
                Must meet same validation requirements as add():
                - Non-empty after trimming
                - Maximum 200 characters
                - Automatically trimmed of whitespace

        Returns:
            CommandResult: Result object with one of the following states:

                Task not found:
                    success=False
                    message="Error: Task with ID {id} not found"
                    data=None

                Invalid description:
                    success=False
                    message="Error: {validation_error}"
                    data=None

                Successfully updated:
                    success=True
                    message="Task {id} updated successfully"
                    data=Task object (with new description)

        Performance:
            O(1) - Single task lookup and in-place mutation

        Example:
            Successful update:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Old description")
                >>> result = commands.update(1, "New description")
                >>> result.success
                True
                >>> result.message
                'Task 1 updated successfully'
                >>> result.data.description
                'New description'

            Preserve completion status:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task")
                >>> commands.complete(1)
                >>> result = commands.update(1, "Updated task")
                >>> result.data.completed
                True

            Task not found:

                >>> commands = TodoCommands(TaskStore())
                >>> result = commands.update(999, "New description")
                >>> result.success
                False
                >>> result.message
                'Error: Task with ID 999 not found'

            Empty description:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task")
                >>> result = commands.update(1, "")
                >>> result.success
                False
                >>> "empty" in result.message.lower()
                True

            Description too long:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task")
                >>> result = commands.update(1, "x" * 201)
                >>> result.success
                False
                >>> "200 characters" in result.message
                True

        Error Handling:
            - Task not found: Returns failure with task-not-found message
            - ValueError from validation: Converted to failure with error text
            - No exception propagates to caller

        Notes:
            - Validation happens in TaskStore.update() via Task creation
            - Completed status is preserved by TaskStore.update()
            - created_at timestamp is preserved
            - Task ID never changes
            - Same description allowed (update with identical text succeeds)
        """
        try:
            # Delegate update to storage layer with validation
            updated_task = self._store.update(task_id, description)

            # Check if task was found
            if updated_task is None:
                return CommandResult(
                    success=False,
                    message=f"Error: Task with ID {task_id} not found",
                    data=None
                )

            # Success: Return confirmation with updated task
            return CommandResult(
                success=True,
                message=f"Task {task_id} updated successfully",
                data=updated_task
            )
        except ValueError as error:
            # Validation failed for new description
            return CommandResult(
                success=False,
                message=f"Error: {str(error)}",
                data=None
            )

    def delete(self, task_id: int) -> CommandResult:
        """Delete a task from storage.

        Permanently removes the specified task from storage. The task ID is
        never reused, even after deletion. This is a destructive operation
        with no undo capability.

        Args:
            task_id (int): The unique identifier of the task to delete.
                Must be a valid task ID that exists in storage.

        Returns:
            CommandResult: Result object with one of the following states:

                Task not found:
                    success=False
                    message="Error: Task with ID {id} not found"
                    data=None

                Successfully deleted:
                    success=True
                    message="Task {id} deleted successfully"
                    data=None

        Performance:
            O(1) - Single dictionary deletion operation

        Example:
            Successful deletion:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task to delete")
                >>> result = commands.delete(1)
                >>> result.success
                True
                >>> result.message
                'Task 1 deleted successfully'

            Verify task removed:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("Task")
                >>> commands.delete(1)
                >>> result = commands.list_all()
                >>> len(result.data)
                0

            Task not found:

                >>> commands = TodoCommands(TaskStore())
                >>> result = commands.delete(999)
                >>> result.success
                False
                >>> result.message
                'Error: Task with ID 999 not found'

            ID not reused after deletion:

                >>> commands = TodoCommands(TaskStore())
                >>> commands.add("First")
                >>> commands.delete(1)
                >>> result = commands.add("Second")
                >>> result.data.id
                2

        Notes:
            - Deletion is permanent (no undo)
            - Deleted task IDs are never reused
            - No data returned in success case (task is gone)
            - No confirmation prompt (CLI layer's responsibility)
            - No cascade operations (tasks are independent)
        """
        # Attempt deletion in storage layer
        deleted = self._store.delete(task_id)

        # Check if task was found and deleted
        if not deleted:
            return CommandResult(
                success=False,
                message=f"Error: Task with ID {task_id} not found",
                data=None
            )

        # Success: Return confirmation
        return CommandResult(
            success=True,
            message=f"Task {task_id} deleted successfully",
            data=None
        )
