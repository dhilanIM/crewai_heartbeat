"""Unit tests for fake-posts FetchMoltbookFeedTool and UpvoteMoltbookPostTool (JSON-backed)."""
import sys
import os
import json
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from upvote_moltbook import FetchMoltbookFeedTool, UpvoteMoltbookPostTool


# ─── FetchMoltbookFeedTool ───────────────────────────────────────────


class TestFetchMoltbookFeedTool:
    """Tests for FetchMoltbookFeedTool reading from a JSON feed file."""

    def setup_method(self):
        self.tool = FetchMoltbookFeedTool()

    def test_reads_posts_from_feed(self, tmp_feed_file):
        """Reads and displays posts from the feed JSON file."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file):
            result = self.tool._run()

        assert "Feed posts:" in result
        assert "test-001" in result
        assert "First Test Post" in result
        assert "alice" in result
        assert "test-002" in result

    def test_empty_feed(self, tmp_path):
        """Returns 'No posts found' when feed is empty."""
        empty_feed = str(tmp_path / "empty_feed.json")
        with open(empty_feed, "w") as f:
            json.dump({"posts": []}, f)

        with patch("upvote_moltbook.FEED_FILE", empty_feed):
            result = self.tool._run()

        assert "No posts found" in result

    def test_missing_feed_file(self, tmp_path):
        """Returns 'No posts found' when feed file doesn't exist."""
        missing = str(tmp_path / "nonexistent.json")
        with patch("upvote_moltbook.FEED_FILE", missing):
            result = self.tool._run()

        assert "No posts found" in result

    def test_sort_by_new(self, tmp_feed_file):
        """Posts sorted by 'new' puts the newest first."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file):
            result = self.tool._run(sort="new")

        lines = result.strip().split("\n")
        # First post should be test-003 (newest created_at)
        assert "test-003" in lines[1]

    def test_limit_posts(self, tmp_feed_file):
        """Respects the limit parameter."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file):
            result = self.tool._run(limit=2)

        lines = [l for l in result.strip().split("\n") if l.startswith(("1.", "2.", "3."))]
        assert len(lines) == 2


# ─── UpvoteMoltbookPostTool ──────────────────────────────────────────


class TestUpvoteMoltbookPostTool:
    """Tests for UpvoteMoltbookPostTool logging upvotes to JSON."""

    def setup_method(self):
        self.tool = UpvoteMoltbookPostTool()

    def test_successful_upvote(self, tmp_feed_file, tmp_log_file):
        """Upvoting an existing post logs it to the activity log."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file), \
             patch("upvote_moltbook.LOG_FILE", tmp_log_file):
            result = self.tool._run(post_id="test-001")

        assert "Successfully upvoted" in result
        assert "test-001" in result

        # Verify the log file
        with open(tmp_log_file, "r") as f:
            data = json.load(f)

        assert len(data["actions"]) == 1
        action = data["actions"][0]
        assert action["action"] == "post_upvoted"
        assert action["post_id"] == "test-001"
        assert action["user"] == "crewai-agent"
        assert "upvoted_at" in action

    def test_upvote_nonexistent_post(self, tmp_feed_file, tmp_log_file):
        """Upvoting a non-existent post returns an error message."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file), \
             patch("upvote_moltbook.LOG_FILE", tmp_log_file):
            result = self.tool._run(post_id="does-not-exist")

        assert "Failed to upvote" in result
        assert "not found" in result

        # Verify nothing was logged
        assert not os.path.exists(tmp_log_file)

    def test_multiple_upvotes_accumulate(self, tmp_feed_file, tmp_log_file):
        """Multiple upvotes are all logged."""
        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file), \
             patch("upvote_moltbook.LOG_FILE", tmp_log_file):
            self.tool._run(post_id="test-001")
            self.tool._run(post_id="test-002")

        with open(tmp_log_file, "r") as f:
            data = json.load(f)

        assert len(data["actions"]) == 2
        assert data["actions"][0]["post_id"] == "test-001"
        assert data["actions"][1]["post_id"] == "test-002"

    def test_feed_not_modified_after_upvote(self, tmp_feed_file, tmp_log_file):
        """The feed file remains unchanged after an upvote."""
        with open(tmp_feed_file, "r") as f:
            original = f.read()

        with patch("upvote_moltbook.FEED_FILE", tmp_feed_file), \
             patch("upvote_moltbook.LOG_FILE", tmp_log_file):
            self.tool._run(post_id="test-001")

        with open(tmp_feed_file, "r") as f:
            after = f.read()

        assert original == after
