"""Unit tests for fake-posts PostToMoltbookTool (JSON-backed)."""
import sys
import os
import json
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from post2moltbook import PostToMoltbookTool, _load_log, _save_log


class TestPostToMoltbookTool:
    """Tests for PostToMoltbookTool that writes to a JSON activity log."""

    def setup_method(self):
        self.tool = PostToMoltbookTool()

    @patch("post2moltbook.LOG_FILE")
    def test_creates_post_in_log(self, mock_log_file, tmp_log_file):
        """Post is logged to the activity log JSON file."""
        mock_log_file.__str__ = lambda x: tmp_log_file
        # Patch LOG_FILE as a string
        with patch("post2moltbook.LOG_FILE", tmp_log_file):
            result = self.tool._run(title="Test Post", content="Hello World")

            assert "Post created successfully!" in result

            # Verify the JSON file was written
            with open(tmp_log_file, "r") as f:
                data = json.load(f)

            assert len(data["actions"]) == 1
            action = data["actions"][0]
            assert action["action"] == "post_created"
            assert action["title"] == "Test Post"
            assert action["content"] == "Hello World"
            assert action["submolt"] == "general"
            assert action["author"] == "crewai-agent"
            assert "id" in action
            assert "created_at" in action

    def test_post_with_custom_submolt(self, tmp_log_file):
        """Post is logged with a custom submolt."""
        with patch("post2moltbook.LOG_FILE", tmp_log_file):
            result = self.tool._run(title="Tech Post", content="About AI", submolt="tech")

            assert "Post created successfully!" in result

            with open(tmp_log_file, "r") as f:
                data = json.load(f)

            assert data["actions"][0]["submolt"] == "tech"

    def test_multiple_posts_accumulate(self, tmp_log_file):
        """Multiple posts are appended, not overwritten."""
        with patch("post2moltbook.LOG_FILE", tmp_log_file):
            self.tool._run(title="First", content="One")
            self.tool._run(title="Second", content="Two")
            self.tool._run(title="Third", content="Three")

            with open(tmp_log_file, "r") as f:
                data = json.load(f)

            assert len(data["actions"]) == 3
            assert data["actions"][0]["title"] == "First"
            assert data["actions"][1]["title"] == "Second"
            assert data["actions"][2]["title"] == "Third"

    def test_handles_empty_log_file(self, tmp_path):
        """Handles an empty/invalid log file gracefully."""
        empty_log = str(tmp_path / "empty_log.json")
        with open(empty_log, "w") as f:
            f.write("")  # Empty file

        with patch("post2moltbook.LOG_FILE", empty_log):
            result = self.tool._run(title="Recovery Post", content="Should work")

            assert "Post created successfully!" in result

            with open(empty_log, "r") as f:
                data = json.load(f)

            assert len(data["actions"]) == 1

    def test_post_returns_unique_id(self, tmp_log_file):
        """Each post gets a unique ID."""
        with patch("post2moltbook.LOG_FILE", tmp_log_file):
            result1 = self.tool._run(title="A", content="1")
            result2 = self.tool._run(title="B", content="2")

            # Extract IDs from result strings
            id1 = result1.split("ID: ")[1]
            id2 = result2.split("ID: ")[1]
            assert id1 != id2
