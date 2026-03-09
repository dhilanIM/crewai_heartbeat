"""Integration tests for MoltbookFlow (crewFlow.py)."""
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

    @patch("builtins.open", mock_open(read_data="Task done\nPROCESSED"))
    @patch("crewFlow.os.path.exists", return_value=True)
    def test_file_already_processed(self, mock_exists):
        """Returns SLEEP when tasks.md contains PROCESSED."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert result == "SLEEP"

    @patch("builtins.open", mock_open(read_data="Create a new post about AI"))
    @patch("crewFlow.os.path.exists", return_value=True)
    def test_file_has_instruction(self, mock_exists):
        """Returns the instruction when there is pending work."""
        flow = MoltbookFlow()
        result = flow.interpret_task_file()
        assert result == "Create a new post about AI"


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
        mock_crew_instance.kickoff.return_value = "Action completed"
        mock_crew_cls.return_value = mock_crew_instance

        flow = MoltbookFlow()
        result = flow.execute_agent_task("Upvote a trending post")

        # Crew was instantiated and kicked off
        mock_crew_cls.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()

        assert result == "Action completed"
