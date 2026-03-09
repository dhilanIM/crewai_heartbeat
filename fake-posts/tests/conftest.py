"""Shared fixtures for fake-posts tests."""
import pytest
import json
import os


@pytest.fixture
def tmp_log_file(tmp_path):
    """Create a temporary activity log file path and patch the module to use it."""
    return str(tmp_path / "agent_activity_log.json")


@pytest.fixture
def tmp_feed_file(tmp_path):
    """Create a temporary feed file with sample posts."""
    feed_path = str(tmp_path / "fake_posts_data.json")
    sample_feed = {
        "posts": [
            {
                "id": "test-001",
                "title": "First Test Post",
                "content": "This is a test post.",
                "submolt": "general",
                "author": "alice",
                "created_at": "2026-03-09T10:00:00"
            },
            {
                "id": "test-002",
                "title": "Second Test Post",
                "content": "Another test post about tech.",
                "submolt": "tech",
                "author": "bob",
                "created_at": "2026-03-09T11:00:00"
            },
            {
                "id": "test-003",
                "title": "Third Test Post",
                "content": "The newest post.",
                "submolt": "general",
                "author": "carol",
                "created_at": "2026-03-09T12:00:00"
            },
        ]
    }
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(sample_feed, f)
    return feed_path
