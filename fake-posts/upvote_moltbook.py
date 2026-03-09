from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
from datetime import datetime


# fake_posts_data.json = the feed (read-only source of posts to browse)
FEED_FILE = os.path.join(os.path.dirname(__file__), "fake_posts_data.json")

# agent_activity_log.json = where the agent logs its actions
LOG_FILE = os.path.join(os.path.dirname(__file__), "agent_activity_log.json")


def _load_feed():
    """Load the feed data (read-only source of posts)."""
    if os.path.exists(FEED_FILE):
        with open(FEED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posts": []}


def _load_log():
    """Load the activity log."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass  # File is empty or invalid, start fresh
    return {"actions": []}


def _save_log(data):
    """Save data back to the activity log."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class FetchMoltbookFeedInput(BaseModel):
    sort: Optional[str] = Field(default="hot", description="Sort order: 'hot', 'new', 'top'.")
    limit: Optional[int] = Field(default=5, description="Number of posts to return.")


class FetchMoltbookFeedTool(BaseTool):
    name: str = "fetch_moltbook_feed"
    description: str = (
        "Fetches the Moltbook feed from the local JSON file. "
        "Use this to browse posts before upvoting one. "
        "Parameters sort and limit are optional."
    )
    args_schema: type = FetchMoltbookFeedInput

    def _run(self, sort: str = "hot", limit: int = 5) -> str:
        data = _load_feed()
        posts = data.get("posts", [])

        if not posts:
            return "No posts found in the feed."

        # Sort posts
        if sort == "new":
            posts = sorted(posts, key=lambda p: p.get("created_at", ""), reverse=True)
        # "hot" = default order

        posts = posts[:limit]

        lines = []
        for i, post in enumerate(posts, 1):
            post_id = post.get("id", "unknown")
            title = post.get("title", "No title")
            author = post.get("author", "unknown")
            lines.append(f'{i}. [ID: {post_id}] "{title}" (by: {author})')

        return "Feed posts:\n" + "\n".join(lines)


class UpvoteMoltbookPostTool(BaseTool):
    name: str = "upvote_moltbook_post"
    description: str = (
        "Upvotes a specific post on Moltbook. "
        "You must provide the post_id of the post to upvote. "
        "The upvote will be recorded in the local JSON file."
    )

    def _run(self, post_id: str) -> str:
        # Check that the post exists in the feed
        feed = _load_feed()
        post_found = any(p.get("id") == post_id for p in feed.get("posts", []))

        if not post_found:
            return f"Failed to upvote: post {post_id} not found."

        # Log the upvote action
        log = _load_log()
        log["actions"].append({
            "action": "post_upvoted",
            "post_id": post_id,
            "user": "crewai-agent",
            "upvoted_at": datetime.now().isoformat(),
        })
        _save_log(log)

        return f"Successfully upvoted post {post_id}!"
