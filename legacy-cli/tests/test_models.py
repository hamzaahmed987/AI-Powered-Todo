"""Tests for Task model."""
from datetime import datetime

import pytest

from todo_cli.models import Task


class TestTaskCreation:
    """Test Task dataclass creation and validation."""

    def test_task_creation_with_valid_description(self):
        """Test creating a task with valid description."""
        task = Task(id=1, description="Buy groceries")
        assert task.id == 1
        assert task.description == "Buy groceries"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_task_rejects_empty_description(self):
        """Test that Task rejects empty description."""
        with pytest.raises(ValueError):
            Task(id=1, description="")

    def test_task_rejects_whitespace_only_description(self):
        """Test that Task rejects whitespace-only description."""
        with pytest.raises(ValueError):
            Task(id=1, description="   ")

    def test_task_rejects_description_over_200_chars(self):
        """Test that Task rejects description over 200 characters."""
        long_description = "x" * 201
        with pytest.raises(ValueError):
            Task(id=1, description=long_description)

    def test_task_accepts_200_char_description(self):
        """Test that Task accepts exactly 200 character description."""
        description_200 = "x" * 200
        task = Task(id=1, description=description_200)
        assert task.description == description_200
        assert len(task.description) == 200

    def test_task_trims_whitespace_from_description(self):
        """Test that Task trims leading and trailing whitespace."""
        task = Task(id=1, description="  Buy groceries  ")
        assert task.description == "Buy groceries"

    def test_task_trims_internal_whitespace_preserved(self):
        """Test that Task preserves internal whitespace while trimming edges."""
        task = Task(id=1, description="  Buy  some  groceries  ")
        assert task.description == "Buy  some  groceries"

    def test_task_default_values(self):
        """Test Task default values for completed and created_at."""
        task = Task(id=1, description="test")
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_task_with_explicit_completed_true(self):
        """Test creating a task with completed=True."""
        task = Task(id=1, description="test", completed=True)
        assert task.completed is True

    def test_task_with_special_characters(self):
        """Test that Task accepts special characters in description."""
        task = Task(id=1, description="Buy 🛒 groceries & 🥕 items!")
        assert task.description == "Buy 🛒 groceries & 🥕 items!"

    def test_task_rejects_description_with_only_spaces(self):
        """Test that Task rejects description with only spaces."""
        with pytest.raises(ValueError):
            Task(id=1, description="     ")

    def test_task_rejects_description_with_tabs_and_newlines(self):
        """Test that Task rejects description with only whitespace (tabs, newlines)."""
        with pytest.raises(ValueError):
            Task(id=1, description="\t\n  ")
