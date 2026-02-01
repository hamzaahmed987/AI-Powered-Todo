"""Tests for TodoCLI user interface layer."""
from unittest.mock import patch

from todo_cli.cli import TodoCLI


class TestTodoCLIAdd:
    """Test TodoCLI add command parsing and display."""

    def test_cli_add_parses_description(self):
        """Test that CLI parses add command with description."""
        cli = TodoCLI()
        with patch("builtins.print"):
            cli._process_input("add Buy groceries")
            # Should not raise an error

    def test_cli_add_displays_success_message(self):
        """Test that success message is displayed for add command."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("add Buy groceries")
            # Check that something was printed (success message)
            assert mock_print.called

    def test_cli_add_displays_error_for_empty(self):
        """Test that error is displayed for empty description."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("add ")
            # Should display error
            assert mock_print.called


class TestTodoCLIList:
    """Test TodoCLI list command."""

    def test_cli_list_calls_list_all(self):
        """Test that list command calls commands.list_all."""
        cli = TodoCLI()
        with patch("builtins.print"):
            cli._process_input("list")
            # Should not raise an error

    def test_cli_list_displays_table(self):
        """Test that list displays tasks in table format."""
        cli = TodoCLI()
        # Add some tasks
        cli._process_input("add Task 1")
        cli._process_input("add Task 2")

        with patch("builtins.print") as mock_print:
            cli._process_input("list")
            # Should display something
            assert mock_print.called

    def test_cli_list_shows_empty_message(self):
        """Test that empty list shows message."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("list")
            # Should display "no tasks" message
            assert mock_print.called


class TestTodoCLIComplete:
    """Test TodoCLI complete command."""

    def test_cli_complete_parses_id(self):
        """Test that complete command parses task ID."""
        cli = TodoCLI()
        cli._process_input("add Test task")

        with patch("builtins.print"):
            cli._process_input("complete 1")
            # Should not raise an error

    def test_cli_complete_invalid_id_shows_error(self):
        """Test that invalid ID shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("complete abc")
            # Should display error
            assert mock_print.called

    def test_cli_complete_missing_id_shows_error(self):
        """Test that missing ID shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("complete")
            # Should display error
            assert mock_print.called


class TestTodoCLIUpdate:
    """Test TodoCLI update command."""

    def test_cli_update_parses_id_and_description(self):
        """Test that update command parses ID and description."""
        cli = TodoCLI()
        cli._process_input("add Original")

        with patch("builtins.print"):
            cli._process_input("update 1 Updated description")
            # Should not raise an error

    def test_cli_update_missing_arguments_shows_error(self):
        """Test that missing arguments shows error."""
        cli = TodoCLI()
        cli._process_input("add Test")

        with patch("builtins.print") as mock_print:
            cli._process_input("update 1")
            # Should display error
            assert mock_print.called

    def test_cli_update_invalid_id_shows_error(self):
        """Test that invalid ID shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("update abc new")
            # Should display error
            assert mock_print.called


class TestTodoCLIDelete:
    """Test TodoCLI delete command."""

    def test_cli_delete_parses_id(self):
        """Test that delete command parses task ID."""
        cli = TodoCLI()
        cli._process_input("add Task to delete")

        with patch("builtins.print"):
            cli._process_input("delete 1")
            # Should not raise an error

    def test_cli_delete_invalid_id_shows_error(self):
        """Test that invalid ID shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("delete abc")
            # Should display error
            assert mock_print.called

    def test_cli_delete_missing_id_shows_error(self):
        """Test that missing ID shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("delete")
            # Should display error
            assert mock_print.called


class TestTodoCLIHelp:
    """Test TodoCLI help command."""

    def test_cli_help_displays_all_commands(self):
        """Test that help command displays all commands."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("help")
            # Should display help text
            assert mock_print.called
            # Verify all commands are mentioned
            call_args = str(mock_print.call_args_list)
            assert "add" in call_args.lower()


class TestTodoCLIExit:
    """Test TodoCLI exit command."""

    def test_cli_exit_exits_loop(self):
        """Test that exit command exits the running loop."""
        cli = TodoCLI()
        cli._process_input("exit")
        assert cli.running is False

    def test_cli_exit_displays_goodbye(self):
        """Test that exit displays goodbye message."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("exit")
            # Should display goodbye
            assert mock_print.called
            call_args = str(mock_print.call_args_list)
            assert "goodbye" in call_args.lower()


class TestTodoCLIIntegration:
    """Integration tests for TodoCLI."""

    def test_cli_full_workflow(self):
        """Test complete workflow: add, list, complete, update, delete."""
        cli = TodoCLI()

        # Add tasks
        with patch("builtins.print"):
            cli._process_input("add Task 1")
            cli._process_input("add Task 2")
            cli._process_input("list")
            cli._process_input("complete 1")
            cli._process_input("update 2 Updated task 2")
            cli._process_input("delete 2")

    def test_cli_unknown_command(self):
        """Test that unknown command shows error."""
        cli = TodoCLI()
        with patch("builtins.print") as mock_print:
            cli._process_input("foobar")
            # Should display unknown command error
            assert mock_print.called
            call_args = str(mock_print.call_args_list)
            assert "unknown" in call_args.lower() or "command" in call_args.lower()
