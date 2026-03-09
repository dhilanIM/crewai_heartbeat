from post2moltbook import PostToMoltbookTool
from upvote_moltbook import FetchMoltbookFeedTool, UpvoteMoltbookPostTool
import os
import sys
from crewai.flow.flow import Flow, start, listen
from crewai import Agent, Task, Crew, LLM
import time
from dotenv import load_dotenv

# Fix Windows console encoding (cp1252 can't handle emoji)
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

HEARTBEAT_INTERVAL = 30  # How often to check (in seconds)
LLM_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "groq/llama-3.3-70b-versatile"


class MoltbookFlow(Flow):

    @start()
    def interpret_task_file(self):
        """Read the .md file and check if there is pending work."""
        file_path = os.path.join(os.path.dirname(__file__), "tasks.md")
        if not os.path.exists(file_path):
            return "SLEEP"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # If the file is empty or already marked as 'PROCESSED'
        if not content or "PROCESSED" in content:
            return "SLEEP"

        print(f"--- New instruction detected: {content} ---")
        return content

    @listen(interpret_task_file)
    def execute_agent_task(self, instruction):
        if instruction == "SLEEP":
            return "No task to execute."

        # The agent receives the instruction as-is from the file
        agent = Agent(
            role="Moltbook Proactive Agent",
            goal="Interpret instructions and interact with Moltbook using ONLY the tools provided to you.",
            backstory=(
                "You are an autonomous agent. You can create posts, fetch the feed, "
                "and upvote posts. All data is stored locally in a JSON file. "
                "You MUST only use the tools provided to you. "
                "Do NOT attempt to search the web or call any tool not explicitly listed."
            ),
            tools=[PostToMoltbookTool(), FetchMoltbookFeedTool(), UpvoteMoltbookPostTool()],
            llm=LLM(model=MODEL, api_key=LLM_API_KEY)
        )

        task = Task(
            description=(
                f"Here is a list of possible tasks: '{instruction}'. "
                "Review the list and PICK the task you find most interesting or relevant. "
                "Use ONLY the tools provided to you. Do NOT search the web. "
                "If the task is about upvoting, first use fetch_moltbook_feed to browse posts, "
                "then pick one and use upvote_moltbook_post with its ID. "
                "If the task is about creating a post, pick an interesting topic yourself "
                "and use post_to_moltbook with submolt='general'."
            ),
            agent=agent,
            expected_output="Confirmation of the action taken and why you chose that task."
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        print("\n========== AGENT RESULT ==========")
        print(result)
        print("==================================\n")

        # Mark file as processed
        file_path = os.path.join(os.path.dirname(__file__), "tasks.md")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n")

        return result


# Main loop execution
if __name__ == "__main__":
    while True:
        MoltbookFlow().kickoff()
        time.sleep(HEARTBEAT_INTERVAL)
