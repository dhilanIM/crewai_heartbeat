"""Unit tests for FetchMoltbookFeedTool and UpvoteMoltbookPostTool."""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from upvote_moltbook import FetchMoltbookFeedTool, UpvoteMoltbookPostTool


# ─── FetchMoltbookFeedTool ───────────────────────────────────────────


class TestFetchMoltbookFeedTool:
    """Tests for FetchMoltbookFeedTool._run()."""

    def setup_method(self):
        self.tool = FetchMoltbookFeedTool()

    @patch("upvote_moltbook.requests.get")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_successful_feed_list_response(self, mock_get):
        """Feed returns a plain list of posts."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"id": "p1", "title": "First Post", "score": 10, "author": "alice"},
            {"id": "p2", "title": "Second Post", "score": 5, "author": "bob"},
        ]
        mock_get.return_value = mock_resp

        result = self.tool._run(sort="hot", limit=5)

        assert "Feed posts:" in result
        assert "p1" in result
        assert "First Post" in result
        assert "alice" in result
        assert "p2" in result

    @patch("upvote_moltbook.requests.get")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_successful_feed_dict_response(self, mock_get):
        """Feed returns a dict with 'posts' key."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "posts": [
                {"id": "p3", "title": "Third", "score": 7, "author": "carol"},
            ]
        }
        mock_get.return_value = mock_resp

        result = self.tool._run()

        assert "p3" in result
        assert "Third" in result

    @patch("upvote_moltbook.requests.get")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_empty_feed(self, mock_get):
        """Feed returns an empty list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = self.tool._run()

        assert "No posts found" in result

    @patch("upvote_moltbook.requests.get")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_feed_api_failure(self, mock_get):
        """Feed API returns a 500 error."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_get.return_value = mock_resp

        result = self.tool._run()

        assert "Failed to fetch feed" in result
        assert "500" in result

    @patch("upvote_moltbook.requests.get")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_author_as_dict(self, mock_get):
        """Author field is a nested dict instead of a string."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"id": "p4", "title": "Nested Author", "score": 3,
             "author": {"username": "dave"}},
        ]
        mock_get.return_value = mock_resp

        result = self.tool._run()

        assert "dave" in result


# ─── UpvoteMoltbookPostTool ──────────────────────────────────────────


class TestUpvoteMoltbookPostTool:
    """Tests for UpvoteMoltbookPostTool._run()."""

    def setup_method(self):
        self.tool = UpvoteMoltbookPostTool()

    @patch("upvote_moltbook.requests.post")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_successful_upvote(self, mock_post):
        """Upvote returns 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = self.tool._run(post_id="abc123")

        assert "Successfully upvoted" in result
        assert "abc123" in result

    @patch("upvote_moltbook.requests.post")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_upvote_failure(self, mock_post):
        """Upvote returns 403 Forbidden."""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_post.return_value = mock_resp

        result = self.tool._run(post_id="abc123")

        assert "Failed to upvote" in result
        assert "403" in result

    @patch("upvote_moltbook.requests.post")
    @patch("upvote_moltbook.API_KEY", "test-key")
    def test_correct_upvote_url(self, mock_post):
        """Verifies the correct endpoint /posts/{id}/upvote is called."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        self.tool._run(post_id="my-post-42")

        call_url = mock_post.call_args[0][0]
        assert "/posts/my-post-42/upvote" in call_url
