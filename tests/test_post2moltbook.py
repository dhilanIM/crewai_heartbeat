"""Unit tests for PostToMoltbookTool."""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from post2moltbook import PostToMoltbookTool


class TestPostToMoltbookTool:
    """Tests for PostToMoltbookTool._run()."""

    def setup_method(self):
        self.tool = PostToMoltbookTool()

    @patch("post2moltbook.requests.post")
    @patch("post2moltbook.API_KEY", "test-key")
    def test_successful_post_flat_response(self, mock_post):
        """Post succeeds with a flat JSON response containing 'id'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "abc123"}
        mock_post.return_value = mock_resp

        result = self.tool._run(title="Hello", content="World")

        assert "Post created successfully!" in result
        assert "abc123" in result

    @patch("post2moltbook.requests.post")
    @patch("post2moltbook.API_KEY", "test-key")
    def test_successful_post_nested_response(self, mock_post):
        """Post succeeds with a nested JSON response {'post': {'id': ...}}."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"post": {"id": "xyz789"}}
        mock_post.return_value = mock_resp

        result = self.tool._run(title="Test", content="Content")

        assert "Post created successfully!" in result
        assert "xyz789" in result

    @patch("post2moltbook.requests.post")
    @patch("post2moltbook.API_KEY", "test-key")
    def test_api_failure(self, mock_post):
        """Post fails with an error status code."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request: missing fields"
        mock_post.return_value = mock_resp

        result = self.tool._run(title="Bad", content="Post")

        assert "Failed" in result
        assert "400" in result

    @patch("post2moltbook.requests.post")
    @patch("post2moltbook.API_KEY", "test-key")
    def test_correct_payload_and_headers(self, mock_post):
        """Verifies the correct URL, headers, and JSON body are sent."""
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "123"}
        mock_post.return_value = mock_resp

        self.tool._run(title="My Title", content="My Content", submolt="tech")

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        assert "/posts" in call_args[0][0] or "/posts" in str(call_args)

        # Check headers
        headers = call_args[1].get("headers", call_args.kwargs.get("headers", {}))
        assert "Bearer test-key" in headers.get("Authorization", "")

        # Check JSON payload
        json_body = call_args[1].get("json", call_args.kwargs.get("json", {}))
        assert json_body["title"] == "My Title"
        assert json_body["content"] == "My Content"
        assert json_body["submolt"] == "tech"
