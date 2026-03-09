from crewai.tools import BaseTool
import requests
import os


API_KEY = os.getenv("MOLTBOOK_API_KEY")
BASE = "https://www.moltbook.com/api/v1"


class PostToMoltbookTool(BaseTool):
    name: str = "post_to_moltbook"
    description: str = (
        "Use this tool to create a new post on Moltbook. "
        "Provide title and content. Submolt is optional (default: general)."
    )

    def _run(self, title: str, content: str, submolt: str = "general") -> str:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"submolt": submolt, "title": title, "content": content}

        response = requests.post(f"{BASE}/posts", json=payload, headers=headers)

        if response.status_code in (200, 201):
            data = response.json()
            post_id = data.get("id") or data.get("post", {}).get("id") or "unknown"
            return f"Post created successfully! ID: {post_id}"
        else:
            return f"Failed: {response.status_code} - {response.text}"