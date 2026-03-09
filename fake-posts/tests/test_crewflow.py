"""Integration tests for fake-posts MoltbookFlow."""
import sys
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crewFlow import MoltbookFlow


class TestInterpretTaskFile:
    """Tests for MoltbookFlow.interpret_task_file()."""

    @patch("crewFlow.os.path.exists", return_value=False)
    def test_file_missing(self, mock_exists):
        """Returns SLEEP when tasks.md does not exist."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert result == "SLEEP"

    @patch("builtins.open", mock_open(read_data=""))
    @patch("crewFlow.os.path.exists", return_value=True)
    def test_file_empty(self, mock_exists):
        """Returns SLEEP when tasks.md is empty."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert result == "SLEEP"

    @patch("builtins.open", mock_open(read_data="Done\nPROCESSED"))
    @patch("crewFlow.os.path.exists", return_value=True)
    def test_file_already_processed(self, mock_exists):
        """Returns SLEEP when tasks.md contains PROCESSED."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert result == "SLEEP"

    @patch("builtins.open", mock_open(read_data="- Create a post\n- Upvote a post"))
    @patch("crewFlow.os.path.exists", return_value=True)
    def test_file_has_task_list(self, mock_exists):
        """Returns the full task list when there is pending work."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert "Create a post" in result
        assert "Upvote a post" in result


class TestExecuteAgentTask:
    """Tests for MoltbookFlow.execute_agent_task()."""

    def test_sleep_instruction(self):
        """Returns early when instruction is SLEEP."""
        flow = MoltbookFlow()
        result = flow.execute_agent_task("SLEEP")
        assert result == "No task to execute."

    @patch("crewFlow.Crew")
    @patch("crewFlow.Task")
    @patch("crewFlow.Agent")
    @patch("builtins.open", mock_open())
    def test_valid_instruction_runs_crew(self, mock_agent_cls, mock_task_cls, mock_crew_cls):
        """Runs the crew and appends to tasks.md for a valid instruction."""
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Task completed"
        mock_crew_cls.return_value = mock_crew_instance

        flow = MoltbookFlow()
        result = flow.execute_agent_task("- Create a post\n- Upvote a post")

        mock_crew_cls.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()
        assert result == "Task completed"
