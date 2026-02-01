"""Todo CLI - A Simple Command-Line Todo Application.

This package provides a lightweight, in-memory todo list application with
comprehensive documentation and colorful output. All business logic is unit-testable
and follows spec-driven development principles.

Attributes:
    __version__ (str): Current version of the application.
    __author__ (str): Author of the application.

Example:
    To start the todo CLI application:

        from todo_cli.main import main
        main()

    Or from the command line:

        python -m todo_cli
        # or
        uv run todo
"""

__version__ = "0.1.0"
__author__ = "Development Team"

__all__ = [
    "__version__",
    "__author__",
]
