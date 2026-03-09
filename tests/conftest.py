"""Shared fixtures for CrewAIFlow tests."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_api_key(monkeypatch):
    """Set a fake MOLTBOOK_API_KEY for all tests."""
    monkeypatch.setenv("MOLTBOOK_API_KEY", "test-api-key-12345")


@pytest.fixture
def mock_success_response():
    """Factory for a successful HTTP response mock."""
    def _make(status_code=200, json_data=None, text="OK"):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data or {}
        resp.text = text
        return resp
    return _make


@pytest.fixture
def mock_error_response():
    """Factory for a failed HTTP response mock."""
    def _make(status_code=400, text="Bad Request"):
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = text
        return resp
    return _make
