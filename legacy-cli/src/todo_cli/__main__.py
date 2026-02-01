"""Allow running the todo-cli application as a module.

This module serves as the entry point for:
    python -m todo_cli

It imports the main function from the main module and executes it,
providing a seamless entry point for the application.

Example:
    From command line:
        $ python -m todo_cli
        Welcome to todo-cli! Type 'help' for available commands.
        >
"""

from todo_cli.main import main

if __name__ == "__main__":
    main()
