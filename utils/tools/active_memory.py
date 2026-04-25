from langchain_core.tools import tool
from utils.logger import edith_logger


# The Ephemeral Whiteboard (Resets every time the script runs)
session_whiteboard = {
    "active_task": "Awaiting instructions.",
    "recent_context": "System just booted up."
}

@tool
def update_whiteboard(active_task: str, recent_context: str) -> str:
    """
    Updates your short-term Core Memory (Whiteboard) for the CURRENT session.
    Call this tool immediately when the user changes the subject, starts a new task, 
    or gives you important context you need to remember for the next few minutes.
    Keep the strings concise. Overwrites previous data.
    """
    global session_whiteboard
    
    session_whiteboard["active_task"] = active_task
    session_whiteboard["recent_context"] = recent_context
    
    edith_logger.info("Current Whiteboard Updated:")
    edith_logger.info(f"Active Task: {session_whiteboard['active_task']}")
    edith_logger.info(f"Recent Context: {session_whiteboard['recent_context']}")
    # Returning a success message helps the LLM know the tool executed properly
    return "Whiteboard successfully updated."