"""Comprehensive Test Suite for Todo-CLI Application.

This package contains all test modules for the todo-cli application.
Tests follow a modular structure, organized by the components they test:

Test Modules:
    test_models: Unit tests for Task data model and validation
    test_store: Unit tests for TaskStore in-memory storage layer
    test_commands: Unit tests for TodoCommands business logic
    test_cli: Integration tests for TodoCLI user interface

All tests are designed to be independent, repeatable, and fast.
Each test module includes docstrings for every test function explaining
what is being tested and why.

Test Execution:
    Run all tests:
        $ uv run pytest tests/ -v

    Run specific test module:
        $ uv run pytest tests/test_models.py -v

    Run with coverage report:
        $ uv run pytest tests/ --cov=src --cov-report=html

    Run specific test:
        $ uv run pytest tests/test_models.py::test_task_creation -v
"""
