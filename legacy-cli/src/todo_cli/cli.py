"""Command-line interface for todo-cli application."""
import sys

from todo_cli.commands import CommandResult, TodoCommands
from todo_cli.models import Task
from todo_cli.db_store import DatabaseTaskStore


class TodoCLI:
    """Interactive command-line interface for the todo application.

    Manages user input, command routing, and output display. Provides a REPL
    (Read-Eval-Print Loop) for users to interact with their tasks.
    """

    HELP_TEXT = """================================================================================
                            AVAILABLE COMMANDS
================================================================================

[CREATE & VIEW]
  add <description>           - Create a new task
  list                        - Show all tasks with status
  show <id>                   - View details of a single task

[MANAGE TASKS]
  complete <id>               - Mark a task as done
  update <id> <description>   - Update task description
  delete <id>                 - Delete a task

[HELP & EXIT]
  help                        - Show this help message
  exit                        - Close the application

================================================================================
EXAMPLES:
  add Buy groceries                    | Add a task
  list                                 | View all tasks
  show 1                               | View task #1
  complete 1                           | Mark task #1 as done
  update 1 Buy milk and eggs          | Update task #1
  delete 1                             | Delete task #1

================================================================================
"""

    def __init__(self) -> None:
        """Initialize TodoCLI with DatabaseTaskStore and TodoCommands.

        Uses database-backed storage to ensure task IDs are persistent
        and assigned by the database engine.
        """
        self._store = DatabaseTaskStore()
        self._commands = TodoCommands(self._store)
        self.running = True

    def _can_read_input(self) -> bool:
        """Check if stdin is available for reading.

        Returns:
            True if stdin is a TTY (terminal), False otherwise.
        """
        return sys.stdin.isatty()

    def run(self) -> None:
        """Start the interactive REPL loop.

        Displays welcome message and continuously reads user input until
        the user exits the application.
        """
        print("\n" + "=" * 80)
        print("                    Welcome to Todo CLI v1.0")
        print("=" * 80 + "\n")
        print("Type a command to get started. Type 'help' for more information.\n")

        while self.running:
            try:
                user_input = input("> ").strip()
                if user_input:
                    self._process_input(user_input)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                self.running = False
            except EOFError:
                print("\nGoodbye!")
                self.running = False

    def _process_input(self, user_input: str) -> None:
        """Parse and route user input to appropriate command handler.

        Args:
            user_input: Raw user input string.
        """
        parts = user_input.split(maxsplit=1)
        if not parts:
            return

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == "add":
            self._handle_add(args)
        elif command == "list":
            self._handle_list(args)
        elif command == "show":
            self._handle_show(args)
        elif command == "complete":
            self._handle_complete(args)
        elif command == "update":
            self._handle_update(args)
        elif command == "delete":
            self._handle_delete(args)
        elif command == "help":
            self._handle_help()
        elif command == "exit":
            self._handle_exit()
        else:
            print("Unknown command. Type 'help' for available commands.")

    def _handle_add(self, args: str) -> None:
        """Handle add command.

        Args:
            args: Description of the task to add.
        """
        if not args.strip():
            msg = "Error: Description cannot be empty"
            result = CommandResult(success=False, message=msg)
        else:
            result = self._commands.add(args.strip())
        self._display_result(result)

    def _handle_list(self, args: str) -> None:
        """Handle list command.

        Args:
            args: Not used for list command.
        """
        result = self._commands.list_all()
        if result.data:
            self._display_tasks(result.data)
        else:
            print(result.message)

    def _handle_show(self, args: str) -> None:
        """Handle show command to display a single task.

        Args:
            args: Task ID to show.
        """
        task_id = self._parse_id(args)
        if task_id is None:
            return

        task = self._store.get(task_id)
        if task is None:
            print(f"[ERROR] Task with ID {task_id} not found")
            return

        self._display_single_task(task)

    def _handle_complete(self, args: str) -> None:
        """Handle complete command.

        Args:
            args: Task ID to mark complete.
        """
        # If no args provided, show all tasks first
        if not args.strip():
            # If not in interactive mode, show error
            if not self._can_read_input():
                print("Error: Missing required argument. Usage: complete <id>")
                return

            result = self._commands.list_all()
            if not result.data:
                print("No tasks to complete.")
                return
            self._display_tasks(result.data)
            # Ask user to enter task ID
            try:
                task_id_input = input("Enter task ID to mark as done: ").strip()
                task_id = self._parse_id(task_id_input)
                if task_id is None:
                    return
            except (EOFError, OSError):
                return
        else:
            task_id = self._parse_id(args)
            if task_id is None:
                return

        result = self._commands.complete(task_id)
        self._display_result(result)

    def _handle_update(self, args: str) -> None:
        """Handle update command.

        Args:
            args: Task ID and new description.
        """
        # If no args provided, show all tasks first
        if not args.strip():
            # If not in interactive mode, show error
            if not self._can_read_input():
                print("Error: Missing required argument. Usage: update <id> <description>")
                return

            result = self._commands.list_all()
            if not result.data:
                print("No tasks to update.")
                return
            self._display_tasks(result.data)
            # Ask user to enter task ID
            try:
                task_id_input = input("Enter task ID to update: ").strip()
                task_id = self._parse_id(task_id_input)
                if task_id is None:
                    return

                # Show current task details
                task = self._store.get(task_id)
                if task is None:
                    print(f"[ERROR] Task with ID {task_id} not found")
                    return

                self._display_single_task(task)

                # Ask for new description
                new_description = input("Enter new description: ").strip()
                if not new_description:
                    print("Error: Description cannot be empty")
                    return

            except (EOFError, OSError):
                return
        else:
            parts = args.split(maxsplit=1)
            task_id = self._parse_id(parts[0])
            if task_id is None:
                return

            # If only ID provided, show task and ask for description
            if len(parts) < 2:
                # If not in interactive mode, show error
                if not self._can_read_input():
                    print("Error: Missing required argument. Usage: update <id> <description>")
                    return

                result = self._commands.list_all()
                if result.data:
                    self._display_tasks(result.data)

                # Show current task details
                task = self._store.get(task_id)
                if task is None:
                    print(f"[ERROR] Task with ID {task_id} not found")
                    return

                self._display_single_task(task)

                # Ask for new description
                try:
                    new_description = input("Enter new description: ").strip()
                    if not new_description:
                        print("Error: Description cannot be empty")
                        return
                except (EOFError, OSError):
                    return
            else:
                new_description = parts[1].strip()

        result = self._commands.update(task_id, new_description)
        self._display_result(result)

    def _handle_delete(self, args: str) -> None:
        """Handle delete command.

        Args:
            args: Task ID to delete.
        """
        # If no args provided, show all tasks first
        if not args.strip():
            # If not in interactive mode, show error
            if not self._can_read_input():
                print("Error: Missing required argument. Usage: delete <id>")
                return

            result = self._commands.list_all()
            if not result.data:
                print("No tasks to delete.")
                return
            self._display_tasks(result.data)
            # Ask user to enter task ID
            try:
                task_id_input = input("Enter task ID to delete: ").strip()
                task_id = self._parse_id(task_id_input)
                if task_id is None:
                    return
            except (EOFError, OSError):
                return
        else:
            task_id = self._parse_id(args)
            if task_id is None:
                return

        result = self._commands.delete(task_id)
        self._display_result(result)

    def _handle_help(self) -> None:
        """Handle help command."""
        print(self.HELP_TEXT)

    def _handle_exit(self) -> None:
        """Handle exit command."""
        print("Goodbye!")
        self.running = False

    def _parse_id(self, arg: str) -> int | None:
        """Parse and validate a task ID from string input.

        Args:
            arg: String to parse as task ID.

        Returns:
            Integer ID if valid, None otherwise (prints error).
        """
        arg = arg.strip()
        if not arg:
            print("Error: Missing required argument. Usage: <command> <id>")
            return None

        try:
            return int(arg)
        except ValueError:
            print("Error: Please provide a valid task ID (number)")
            return None

    def _display_result(self, result: CommandResult) -> None:
        """Display command result to user.

        Args:
            result: CommandResult to display.
        """
        if result.success:
            print(f"[OK] {result.message}")
        else:
            print(f"[ERROR] {result.message}")

    def _display_tasks(self, tasks: list[Task]) -> None:
        """Display tasks in formatted table.

        Task IDs are displayed with zero-padding (01, 02, 03...) based on
        the maximum ID in the list for consistent formatting.

        Args:
            tasks: List of Task objects to display.
        """
        if not tasks:
            print("\nNo tasks found. Create your first task with: add <description>\n")
            return

        # Calculate statistics
        completed_count = sum(1 for task in tasks if task.completed)
        pending_count = len(tasks) - completed_count

        # Determine padding width for task IDs (e.g., "01", "02" for up to 99 tasks)
        max_id = max(task.id for task in tasks) if tasks else 0
        id_width = len(str(max_id))

        # Print header with summary
        print("\n" + "=" * 80)
        print(f"TASK LIST | Total: {len(tasks)} | Done: {completed_count} | Pending: {pending_count}")
        print("=" * 80)

        # Print column headers
        print(f"{'ID':<{id_width + 1}} {'STATUS':<10} {'DESCRIPTION':<53} {'DATE':<10}")
        print("-" * 80)

        # Print tasks
        for task in tasks:
            # Truncate description to fit in column
            desc = task.description
            if len(desc) > 51:
                desc = desc[:48] + "..."

            # Format status with visual indicator (ASCII-friendly)
            if task.completed:
                status_pad = "[DONE]"
            else:
                status_pad = "[TODO]"

            # Format creation date
            created_date = task.created_at.strftime("%m/%d")

            # Format task ID with zero-padding
            formatted_id = str(task.id).zfill(2)

            print(f"{formatted_id:<{id_width + 1}} {status_pad:<10} {desc:<53} {created_date:<10}")

        print("=" * 80)

        # Print action hints
        if pending_count > 0:
            print(f"\nHint: Mark task done with: complete <id>")
        if len(tasks) > 0:
            print(f"      Update a task with: update <id> <new description>")
            print(f"      Delete a task with: delete <id>")
        print()

    def _display_single_task(self, task: Task) -> None:
        """Display details of a single task.

        Task ID is displayed with zero-padding (01, 02, 03...) for consistency.

        Args:
            task: Task object to display.
        """
        # Format status
        status = "DONE" if task.completed else "TODO"
        status_display = "[DONE]" if task.completed else "[TODO]"

        # Format task ID with zero-padding
        formatted_id = str(task.id).zfill(2)

        # Print task details
        print("\n" + "=" * 80)
        print(f"TASK #{formatted_id}")
        print("=" * 80)
        print(f"Status:      {status_display}")
        print(f"Description: {task.description}")
        print(f"Created:     {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Print action hints
        if not task.completed:
            print(f"\nYou can: complete {task.id} (mark as done)")
        print(f"         update {task.id} <new description> (change description)")
        print(f"         delete {task.id} (remove this task)")
        print()
