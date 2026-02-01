"""Tests for TodoCommands business logic layer."""
from todo_cli.commands import CommandResult, TodoCommands
from todo_cli.models import Task
from todo_cli.store import TaskStore


class TestCommandResult:
    """Test CommandResult dataclass."""

    def test_command_result_creation(self):
        """Test creating a CommandResult."""
        result = CommandResult(success=True, message="Test message")
        assert result.success is True
        assert result.message == "Test message"
        assert result.data is None

    def test_command_result_with_data(self):
        """Test CommandResult with data."""
        task = Task(id=1, description="Test")
        result = CommandResult(success=True, message="Success", data=task)
        assert result.success is True
        assert result.message == "Success"
        assert result.data is task


class TestTodoCommandsAdd:
    """Test TodoCommands.add() method."""

    def test_add_creates_task_successfully(self):
        """Test that add creates a task and returns success."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.add("Buy groceries")

        assert result.success is True
        assert "Task added successfully" in result.message
        assert "ID: 1" in result.message

    def test_add_returns_task_data(self):
        """Test that add returns the created task in data field."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.add("Buy groceries")

        assert result.data is not None
        assert isinstance(result.data, Task)
        assert result.data.id == 1
        assert result.data.description == "Buy groceries"
        assert result.data.completed is False

    def test_add_rejects_empty_description(self):
        """Test that add rejects empty description."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.add("")

        assert result.success is False
        assert "Error" in result.message
        assert "empty" in result.message.lower()

    def test_add_rejects_whitespace_only(self):
        """Test that add rejects whitespace-only description."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.add("   ")

        assert result.success is False
        assert "Error" in result.message

    def test_add_rejects_over_200_chars(self):
        """Test that add rejects description over 200 characters."""
        store = TaskStore()
        commands = TodoCommands(store)

        long_desc = "x" * 201
        result = commands.add(long_desc)

        assert result.success is False
        assert "Error" in result.message
        assert "200" in result.message

    def test_add_increments_task_ids(self):
        """Test that successive adds have incremented IDs."""
        store = TaskStore()
        commands = TodoCommands(store)

        result1 = commands.add("First task")
        result2 = commands.add("Second task")
        result3 = commands.add("Third task")

        assert result1.data.id == 1
        assert result2.data.id == 2
        assert result3.data.id == 3

    def test_add_error_messages_match_spec(self):
        """Test that error messages match specification."""
        store = TaskStore()
        commands = TodoCommands(store)

        # Empty description
        result = commands.add("")
        assert "Error" in result.message
        assert "empty" in result.message.lower()

        # Over 200 chars
        result = commands.add("x" * 201)
        assert "Error" in result.message
        assert "200" in result.message


class TestTodoCommandsListAll:
    """Test TodoCommands.list_all() method."""

    def test_list_all_returns_empty_message(self):
        """Test that list_all returns empty message when no tasks."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.list_all()

        assert result.success is True
        assert result.data == []
        # Message should indicate no tasks
        assert "No tasks" in result.message or "empty" in result.message.lower()

    def test_list_all_returns_tasks(self):
        """Test that list_all returns all tasks."""
        store = TaskStore()
        commands = TodoCommands(store)

        # Add some tasks
        commands.add("Task 1")
        commands.add("Task 2")
        commands.add("Task 3")

        result = commands.list_all()

        assert result.success is True
        assert len(result.data) == 3
        assert all(isinstance(task, Task) for task in result.data)

    def test_list_all_maintains_order(self):
        """Test that list_all returns tasks in ID order."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("First")
        commands.add("Second")
        commands.add("Third")

        list_result = commands.list_all()
        tasks = list_result.data

        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3


class TestTodoCommandsComplete:
    """Test TodoCommands.complete() method."""

    def test_complete_marks_task_done(self):
        """Test that complete marks a task as done."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task to complete")
        result = commands.complete(1)

        assert result.success is True
        assert "complete" in result.message.lower() or "done" in result.message.lower()

    def test_complete_sets_completed_flag(self):
        """Test that completed flag is set."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task")
        commands.complete(1)

        # Verify task is completed
        task = store.get(1)
        assert task.completed is True

    def test_complete_already_complete_returns_info(self):
        """Test that completing already-complete task returns info."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task")
        commands.complete(1)
        result = commands.complete(1)

        assert result.success is True
        msg_lower = result.message.lower()
        assert "already" in msg_lower or "complete" in msg_lower

    def test_complete_nonexistent_task_returns_error(self):
        """Test that completing non-existent task returns error."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.complete(999)

        assert result.success is False
        assert "Error" in result.message
        assert "not found" in result.message.lower()


class TestTodoCommandsUpdate:
    """Test TodoCommands.update() method."""

    def test_update_changes_description(self):
        """Test that update changes task description."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Original")
        result = commands.update(1, "Updated")

        assert result.success is True
        assert "updated" in result.message.lower()
        assert result.data.description == "Updated"

    def test_update_preserves_completed_status(self):
        """Test that update preserves completed status."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task")
        commands.complete(1)
        result = commands.update(1, "Updated")

        assert result.data.completed is True

    def test_update_rejects_empty_description(self):
        """Test that update rejects empty description."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Original")
        result = commands.update(1, "")

        assert result.success is False
        assert "Error" in result.message

    def test_update_rejects_over_200_chars(self):
        """Test that update rejects description over 200 chars."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Original")
        result = commands.update(1, "x" * 201)

        assert result.success is False
        assert "Error" in result.message

    def test_update_nonexistent_task_returns_error(self):
        """Test that updating non-existent task returns error."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.update(999, "New description")

        assert result.success is False
        assert "Error" in result.message
        assert "not found" in result.message.lower()


class TestTodoCommandsDelete:
    """Test TodoCommands.delete() method."""

    def test_delete_removes_task(self):
        """Test that delete removes a task."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task to delete")
        result = commands.delete(1)

        assert result.success is True
        assert "deleted" in result.message.lower()

    def test_delete_task_not_in_store(self):
        """Test that deleted task is no longer in store."""
        store = TaskStore()
        commands = TodoCommands(store)

        commands.add("Task to delete")
        commands.delete(1)

        assert store.get(1) is None

    def test_delete_nonexistent_task_returns_error(self):
        """Test that deleting non-existent task returns error."""
        store = TaskStore()
        commands = TodoCommands(store)

        result = commands.delete(999)

        assert result.success is False
        assert "Error" in result.message
        assert "not found" in result.message.lower()
