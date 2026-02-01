"""Main entry point for the todo CLI application."""
from todo_cli.cli import TodoCLI


def main() -> None:
    """Run the todo CLI application."""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()
