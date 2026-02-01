"""In-Memory Task Storage Layer for Todo-CLI Application.

This module provides the TaskStore class, which manages all task storage and
retrieval operations. It implements a complete CRUD (Create, Read, Update, Delete)
interface with sequential ID auto-generation and persistence within the application
session.

The storage layer sits between the data model (Task) and the business logic layer
(TodoCommands), providing:
- Automatic sequential ID generation (1, 2, 3, ...)
- O(1) task lookup by ID using dict-based storage
- Task lifecycle management (create, read, update, delete, complete)
- Data integrity through Task validation

Design Pattern: Repository Pattern
    TaskStore acts as a repository for Task objects, abstracting the storage
    mechanism from business logic. If persistence were needed later, the
    storage mechanism could be swapped without changing the interface.

Performance: All operations are O(1) average case
    - Add: Insert into dict by auto-incremented ID
    - Get: Direct dict lookup
    - Delete: Direct dict deletion
    - Update: Direct object mutation
    - Mark Complete: Direct flag update

Limitations:
    - In-memory only: Data lost on application exit
    - Single-threaded: No thread-safety guarantees
    - Single-user: No conflict resolution for concurrent access

Classes:
    TaskStore: Main repository for managing tasks

Example:
    Creating and using TaskStore:

        >>> from store import TaskStore
        >>> store = TaskStore()
        >>> task1 = store.add("Buy groceries")
        >>> task1.id
        1
        >>> task2 = store.add("Clean house")
        >>> task2.id
        2
        >>> all_tasks = store.get_all()
        >>> len(all_tasks)
        2
        >>> store.mark_complete(1)
        >>> store.get(1).completed
        True
        >>> store.delete(2)
        True
        >>> len(store.get_all())
        1
"""


from todo_cli.models import Task


class TaskStore:
    """In-memory repository for managing Task objects with CRUD operations.

    TaskStore manages the complete lifecycle of Task objects during an application
    session. It provides:
    - Create: add() - Create new tasks with auto-incremented IDs
    - Read: get(), get_all() - Retrieve tasks by ID or get all tasks
    - Update: update() - Modify task descriptions (preserves completion status)
    - Delete: delete() - Remove tasks by ID
    - Complete: mark_complete() - Mark tasks as done

    Internal State:
        _tasks (dict[int, Task]): Dictionary mapping task IDs to Task objects.
            Provides O(1) lookup and deletion by ID.

        _next_id (int): Counter for next sequential ID to assign.
            Starts at 1 and increments with each new task.
            Never decremented, ensuring IDs are unique per session.

    Attributes:
        _tasks: Internal task storage (dict[int, Task])
        _next_id: Next ID to assign (int)

    Example:
        Complete workflow example:

            >>> store = TaskStore()
            >>> # Create tasks
            >>> t1 = store.add("Task 1")
            >>> t2 = store.add("Task 2")
            >>> t1.id, t2.id
            (1, 2)
            >>> # Retrieve tasks
            >>> store.get(1).description
            'Task 1'
            >>> # Update task
            >>> updated = store.update(1, "Updated Task 1")
            >>> updated.description
            'Updated Task 1'
            >>> # Mark complete
            >>> store.mark_complete(1)
            >>> store.get(1).completed
            True
            >>> # Delete task
            >>> store.delete(2)
            True
            >>> # Check remaining
            >>> len(store.get_all())
            1

    Notes:
        - All methods operate on Task objects, which have their own validation
        - ID uniqueness is guaranteed within a session
        - Task references are returned directly (caller can mutate them)
        - No transaction support or rollback capabilities
    """

    def __init__(self) -> None:
        """Initialize TaskStore with empty task dictionary.

        Creates a new empty in-memory storage for tasks. The store initializes
        with no tasks and _next_id set to 1, ready to assign sequential IDs
        starting from 1 for the first task.

        Attributes initialized:
            _tasks (dict[int, Task]): Empty dictionary for task storage
            _next_id (int): Counter starting at 1 for first task ID

        Example:
            >>> store = TaskStore()
            >>> store.get_all()
            []
        """
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, description: str) -> Task:
        """Create and store a new task with auto-incremented ID.

        Creates a Task object with the provided description, assigning it the
        next sequential ID from _next_id. The task is immediately stored and
        _next_id is incremented for the next task.

        Task validation happens in Task.__post_init__, so invalid descriptions
        will raise ValueError before the task is stored.

        Args:
            description (str): Task description (1-200 chars, non-empty required).
                Will be trimmed of whitespace and validated.
                Max length is 200 characters.

        Returns:
            Task: The newly created Task object with auto-assigned ID.
                The returned task is the same object stored internally,
                so modifications will affect stored state.

        Raises:
            ValueError: If description fails Task validation:
                - Empty or whitespace-only description
                - Description exceeds 200 characters

        Performance:
            O(1) - Single dictionary insertion and counter increment

        Example:
            >>> store = TaskStore()
            >>> task = store.add("Buy groceries")
            >>> task.id
            1
            >>> task.description
            'Buy groceries'
            >>> task.completed
            False
            >>> next_task = store.add("Clean house")
            >>> next_task.id
            2

            With invalid description:
                >>> store.add("")  # doctest: +SKIP
                Traceback (most recent call last):
                    ...
                ValueError: Task description cannot be empty or whitespace-only
        """
        # Create Task with auto-assigned ID (raises ValueError if invalid)
        task = Task(id=self._next_id, description=description)

        # Store the task in the internal dictionary
        self._tasks[self._next_id] = task

        # Increment counter for next task's ID
        self._next_id += 1

        return task

    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Performs a dictionary lookup to find the task with the specified ID.
        Returns None if the task does not exist.

        Args:
            task_id (int): ID of the task to retrieve.

        Returns:
            Optional[Task]: The Task object if found, None if not found.
                The returned object is the same object stored internally,
                so modifications will affect stored state.

        Performance:
            O(1) - Single dictionary lookup

        Example:
            >>> store = TaskStore()
            >>> task = store.add("Task 1")
            >>> retrieved = store.get(1)
            >>> retrieved.description
            'Task 1'
            >>> store.get(999) is None
            True
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Retrieve all tasks in creation order.

        Returns a list of all Task objects currently stored, maintaining
        creation order by ID. The list is a copy of the internal dict values,
        so modifying the list won't affect storage, but modifying individual
        Task objects will.

        Returns:
            list[Task]: List of all Task objects, sorted by ID (creation order).
                Empty list if no tasks exist.
                The returned Task objects are references to stored objects,
                so modifications will affect stored state.

        Performance:
            O(n) - Iterate all tasks to build list (where n = task count)

        Example:
            >>> store = TaskStore()
            >>> store.get_all()
            []
            >>> store.add("Task 1")
            >>> store.add("Task 2")
            >>> tasks = store.get_all()
            >>> len(tasks)
            2
            >>> [t.description for t in tasks]
            ['Task 1', 'Task 2']
        """
        return list(self._tasks.values())

    def update(self, task_id: int, description: str) -> Task | None:
        """Update a task's description.

        Finds the task by ID and updates its description while preserving
        other attributes (ID, completed status, created_at). The new description
        is validated the same way as during task creation.

        Args:
            task_id (int): ID of the task to update.
            description (str): New task description (1-200 chars, non-empty).
                Will be trimmed and validated like task creation.

        Returns:
            Optional[Task]: The updated Task object if found, None if not found.
                Returns the same Task object stored internally,
                so modifications will affect stored state.

        Raises:
            ValueError: If new description fails Task validation:
                - Empty or whitespace-only description
                - Description exceeds 200 characters

        Performance:
            O(1) - Single dictionary lookup and in-place mutation

        Example:
            >>> store = TaskStore()
            >>> task = store.add("Old description")
            >>> updated = store.update(1, "New description")
            >>> updated.description
            'New description'
            >>> updated.id
            1
            >>> updated.completed  # Preserved
            False
            >>> store.update(999, "New") is None
            True

            With invalid description:
                >>> store.update(1, "")  # doctest: +SKIP
                Traceback (most recent call last):
                    ...
                ValueError: Task description cannot be empty or whitespace-only
        """
        # Look up the task by ID
        task = self._tasks.get(task_id)
        if task is None:
            return None

        # Validate the new description using Task's validation logic
        # Create temporary Task to validate, then extract trimmed description
        temp = Task(id=-1, description=description)

        # If validation passed, update the task's description in-place
        task.description = temp.description
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Removes the task from storage permanently. The task ID is never reused
        in the current session.

        Args:
            task_id (int): ID of the task to delete.

        Returns:
            bool: True if task was found and deleted, False if not found.

        Performance:
            O(1) - Single dictionary deletion operation

        Example:
            >>> store = TaskStore()
            >>> task = store.add("Task to delete")
            >>> store.delete(1)
            True
            >>> store.get(1) is None
            True
            >>> store.delete(999)
            False
            >>> len(store.get_all())
            0
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def mark_complete(self, task_id: int) -> Task | None:
        """Mark a task as complete.

        Sets a task's completed status to True. This operation is idempotent:
        calling mark_complete on an already-complete task has no effect and
        still returns the task.

        Args:
            task_id (int): ID of the task to mark as complete.

        Returns:
            Optional[Task]: The Task object with completed=True if found,
                None if not found.
                Returns the same Task object stored internally,
                so modifications will affect stored state.

        Performance:
            O(1) - Single dictionary lookup and boolean flag update

        Idempotency:
            Calling mark_complete multiple times on the same task is safe:

                >>> store = TaskStore()
                >>> task = store.add("Task")
                >>> store.mark_complete(1)
                >>> store.get(1).completed
                True
                >>> store.mark_complete(1)  # No change needed
                >>> store.get(1).completed
                True

        Example:
            >>> store = TaskStore()
            >>> task = store.add("Task to complete")
            >>> task.completed
            False
            >>> completed = store.mark_complete(1)
            >>> completed.completed
            True
            >>> store.get(1).completed
            True
            >>> store.mark_complete(999) is None
            True
        """
        # Look up the task by ID
        task = self._tasks.get(task_id)
        if task is None:
            return None

        # Update the task's completed flag in-place
        task.completed = True
        return task
