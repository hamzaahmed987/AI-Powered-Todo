"""Tests for TaskStore storage layer."""
import pytest

from todo_cli.models import Task
from todo_cli.store import TaskStore


class TestTaskStoreAdd:
    """Test TaskStore.add() method."""

    def test_add_creates_task_with_next_id(self):
        """Test that add() creates task with correct sequential ID."""
        store = TaskStore()
        task1 = store.add("First task")
        assert task1.id == 1
        assert task1.description == "First task"
        assert task1.completed is False

        task2 = store.add("Second task")
        assert task2.id == 2
        assert task2.description == "Second task"

    def test_add_increments_next_id_sequentially(self):
        """Test that multiple adds produce sequential IDs."""
        store = TaskStore()
        ids = []
        for i in range(5):
            task = store.add(f"Task {i+1}")
            ids.append(task.id)
        assert ids == [1, 2, 3, 4, 5]

    def test_add_returns_task_instance(self):
        """Test that add() returns a Task instance."""
        store = TaskStore()
        task = store.add("Test task")
        assert isinstance(task, Task)

    def test_add_stores_task_in_internal_dict(self):
        """Test that added task is stored and retrievable."""
        store = TaskStore()
        task = store.add("Test task")
        retrieved = store.get(task.id)
        assert retrieved == task


class TestTaskStoreGet:
    """Test TaskStore.get() method."""

    def test_get_returns_task_or_none(self):
        """Test that get() returns Task for existing ID and None for missing."""
        store = TaskStore()
        task = store.add("Test task")

        # Existing task
        retrieved = store.get(task.id)
        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.description == "Test task"

        # Non-existent task
        missing = store.get(999)
        assert missing is None

    def test_get_returns_same_task_instance(self):
        """Test that get() returns the exact same Task instance."""
        store = TaskStore()
        task = store.add("Test task")
        retrieved = store.get(task.id)
        assert retrieved is task


class TestTaskStoreGetAll:
    """Test TaskStore.get_all() method."""

    def test_get_all_returns_empty_list_for_empty_store(self):
        """Test that get_all() returns empty list when no tasks."""
        store = TaskStore()
        tasks = store.get_all()
        assert tasks == []

    def test_get_all_returns_all_tasks(self):
        """Test that get_all() returns all stored tasks."""
        store = TaskStore()
        added = []
        for i in range(3):
            task = store.add(f"Task {i+1}")
            added.append(task)

        retrieved = store.get_all()
        assert len(retrieved) == 3
        assert retrieved == added

    def test_get_all_returns_tasks_in_order(self):
        """Test that get_all() returns tasks in creation order (by ID)."""
        store = TaskStore()
        for i in range(5):
            store.add(f"Task {i}")
        all_tasks = store.get_all()

        assert len(all_tasks) == 5
        for i, task in enumerate(all_tasks):
            assert task.id == i + 1


class TestTaskStoreUpdate:
    """Test TaskStore.update() method."""

    def test_update_changes_description(self):
        """Test that update() changes task description."""
        store = TaskStore()
        task = store.add("Original description")

        updated = store.update(task.id, "New description")
        assert updated is not None
        assert updated.description == "New description"

    def test_update_returns_none_for_missing_id(self):
        """Test that update() returns None for non-existent task."""
        store = TaskStore()
        result = store.update(999, "New description")
        assert result is None

    def test_update_rejects_empty_description(self):
        """Test that update() rejects empty description."""
        store = TaskStore()
        task = store.add("Original")

        with pytest.raises(ValueError):
            store.update(task.id, "")

    def test_update_preserves_id(self):
        """Test that update() preserves task ID."""
        store = TaskStore()
        task = store.add("Original")
        original_id = task.id

        updated = store.update(task.id, "Updated")
        assert updated.id == original_id

    def test_update_preserves_completed_status(self):
        """Test that update() preserves completed status."""
        store = TaskStore()
        task = store.add("Original")
        store.mark_complete(task.id)

        updated = store.update(task.id, "Updated")
        assert updated.completed is True

    def test_update_modifies_stored_task(self):
        """Test that update() modifies the stored task instance."""
        store = TaskStore()
        task = store.add("Original")

        updated = store.update(task.id, "Updated")
        retrieved = store.get(task.id)
        assert retrieved.description == "Updated"
        assert updated is retrieved


class TestTaskStoreDelete:
    """Test TaskStore.delete() method."""

    def test_delete_removes_task_and_returns_true(self):
        """Test that delete() removes task and returns True."""
        store = TaskStore()
        task = store.add("Task to delete")

        result = store.delete(task.id)
        assert result is True
        assert store.get(task.id) is None

    def test_delete_returns_false_for_missing_id(self):
        """Test that delete() returns False for non-existent task."""
        store = TaskStore()
        result = store.delete(999)
        assert result is False

    def test_delete_removes_from_get_all(self):
        """Test that deleted task no longer appears in get_all()."""
        store = TaskStore()
        task1 = store.add("Task 1")
        task2 = store.add("Task 2")
        task3 = store.add("Task 3")

        store.delete(task2.id)
        remaining = store.get_all()

        assert len(remaining) == 2
        assert task1 in remaining
        assert task3 in remaining
        assert task2 not in remaining


class TestTaskStoreMarkComplete:
    """Test TaskStore.mark_complete() method."""

    def test_mark_complete_sets_completed_flag(self):
        """Test that mark_complete() sets completed to True."""
        store = TaskStore()
        task = store.add("Task to complete")

        completed = store.mark_complete(task.id)
        assert completed is not None
        assert completed.completed is True

    def test_mark_complete_returns_none_for_missing_id(self):
        """Test that mark_complete() returns None for non-existent task."""
        store = TaskStore()
        result = store.mark_complete(999)
        assert result is None

    def test_mark_complete_is_idempotent(self):
        """Test that mark_complete() can be called multiple times safely."""
        store = TaskStore()
        task = store.add("Task")

        result1 = store.mark_complete(task.id)
        result2 = store.mark_complete(task.id)

        assert result1.completed is True
        assert result2.completed is True
        assert result1.id == result2.id

    def test_mark_complete_modifies_stored_task(self):
        """Test that mark_complete() modifies the stored task."""
        store = TaskStore()
        task = store.add("Task")

        store.mark_complete(task.id)
        retrieved = store.get(task.id)
        assert retrieved.completed is True

    def test_mark_complete_returns_same_instance(self):
        """Test that mark_complete() returns the same task instance."""
        store = TaskStore()
        task = store.add("Task")

        completed = store.mark_complete(task.id)
        assert completed is task


class TestTaskStoreIntegration:
    """Integration tests for TaskStore."""

    def test_full_lifecycle(self):
        """Test complete task lifecycle: add, get, update, complete, delete."""
        store = TaskStore()

        # Add
        task = store.add("Buy groceries")
        assert task.id == 1

        # Get
        retrieved = store.get(1)
        assert retrieved.description == "Buy groceries"
        assert retrieved.completed is False

        # Update
        updated = store.update(1, "Buy organic groceries")
        assert updated.description == "Buy organic groceries"

        # Complete
        completed = store.mark_complete(1)
        assert completed.completed is True

        # Delete
        deleted = store.delete(1)
        assert deleted is True
        assert store.get(1) is None

    def test_multiple_tasks_independent_state(self):
        """Test that multiple tasks maintain independent state."""
        store = TaskStore()

        task1 = store.add("Task 1")
        task2 = store.add("Task 2")
        task3 = store.add("Task 3")

        # Mark only task2 complete
        store.mark_complete(task2.id)

        assert store.get(task1.id).completed is False
        assert store.get(task2.id).completed is True
        assert store.get(task3.id).completed is False

        # Update only task1
        store.update(task1.id, "Updated task 1")

        assert store.get(task1.id).description == "Updated task 1"
        assert store.get(task2.id).description == "Task 2"
        assert store.get(task3.id).description == "Task 3"

    def test_id_generation_continues_after_delete(self):
        """Test that ID generation continues sequentially even after deletion."""
        store = TaskStore()

        store.add("Task 1")  # id=1
        task2 = store.add("Task 2")  # id=2
        store.add("Task 3")  # id=3

        # Delete task2
        store.delete(task2.id)

        # Add new task - should get id=4, not id=2
        task4 = store.add("Task 4")
        assert task4.id == 4
