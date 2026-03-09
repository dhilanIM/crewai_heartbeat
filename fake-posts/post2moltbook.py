from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
import uuid
from datetime import datetime


# agent_activity_log.json = where the agent logs its actions (posts created, upvotes)
LOG_FILE = os.path.join(os.path.dirname(__file__), "agent_activity_log.json")


def _load_log():
    """Load the activity log, or return an empty structure."""
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


class PostToMoltbookInput(BaseModel):
    title: str = Field(..., description="Title of the post")
    content: str = Field(..., description="Content/body of the post")
    submolt: str = Field(default="general", description="The submolt to post in")


class PostToMoltbookTool(BaseTool):
    name: str = "post_to_moltbook"
    description: str = (
        "Use this tool to create a new post on Moltbook. "
        "You MUST provide 'title' and 'content' as arguments. "
        "'submolt' is optional (default: general). "
        "The post will be saved to a local JSON file."
    )
    args_schema: type = PostToMoltbookInput

    def _run(self, title: str, content: str, submolt: str = "general") -> str:
        log = _load_log()

        post_id = str(uuid.uuid4())[:8]
        log["actions"].append({
            "action": "post_created",
            "id": post_id,
            "title": title,
            "content": content,
            "submolt": submolt,
            "author": "crewai-agent",
            "created_at": datetime.now().isoformat(),
        })

        _save_log(log)

        return f"Post created successfully! ID: {post_id}"
