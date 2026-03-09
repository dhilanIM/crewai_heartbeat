from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import requests
import os


API_KEY = os.getenv("MOLTBOOK_API_KEY")
BASE = "https://www.moltbook.com/api/v1"


class FetchMoltbookFeedInput(BaseModel):
    sort: Optional[str] = Field(default="hot", description="Sort order for the feed, e.g. 'hot', 'new', 'top'.")
    limit: Optional[int] = Field(default=5, description="Number of posts to return.")


class FetchMoltbookFeedTool(BaseTool):
    name: str = "fetch_moltbook_feed"
    description: str = (
        "Fetches the Moltbook feed and returns a list of posts. "
        "Use this to browse posts before upvoting one. "
        "Parameters sort and limit are optional with defaults 'hot' and 5."
    )
    args_schema: type = FetchMoltbookFeedInput

    def _run(self, sort: str = "hot", limit: int = 5) -> str:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
        }
        params = {"sort": sort, "limit": limit}

        response = requests.get(f"{BASE}/feed", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            posts = data if isinstance(data, list) else data.get("posts", data.get("data", []))

            if not posts:
                return "No posts found in the feed."

            lines = []
            for i, post in enumerate(posts, 1):
                post_id = post.get("id") or post.get("_id") or "unknown"
                title = post.get("title", "No title")
                score = post.get("score", post.get("votes", "?"))
                author = post.get("author", post.get("username", "unknown"))
                if isinstance(author, dict):
                    author = author.get("username", "unknown")
                lines.append(f"{i}. [ID: {post_id}] \"{title}\" (score: {score}, by: {author})")

            return "Feed posts:\n" + "\n".join(lines)
        else:
            return f"Failed to fetch feed: {response.status_code} - {response.text}"


class UpvoteMoltbookPostTool(BaseTool):
    name: str = "upvote_moltbook_post"
    description: str = (
        "Upvotes a specific post on Moltbook. "
        "You must provide the post_id of the post to upvote."
    )

    def _run(self, post_id: str) -> str:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(f"{BASE}/posts/{post_id}/upvote", headers=headers)

        if response.status_code in (200, 201):
            return f"Successfully upvoted post {post_id}!"
        else:
            return f"Failed to upvote: {response.status_code} - {response.text}"
