import asyncio
import os
import platform
from dotenv import load_dotenv

from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


from src.memory_manager import MemoryManager
from utils.helpers import read_yaml_config
from utils.tools.os_tools import check_folder, create_file, execute_terminal
from utils.tools.tools import launch_application, open_website, check_vital_signs
from utils.logger import edith_logger


load_dotenv()  # Load environment variables from .env file

# --- 1. The Backpack ---
class AgentState(TypedDict):
    # 'add_messages' is the magic word here. 
    # It tells LangGraph: "When new messages arrive, APPEND them to the list, don't overwrite it."
    messages : Annotated[list[BaseMessage], add_messages]

def router(state: AgentState):
    """
    Looks at the Manager's last message.
    If it asked for a tool, route to 'worker'.
    If it just talked, route to END.
    """
    edith_logger.info(f"Router is checking the Manager's last message to decide where to route next...")
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        edith_logger.debug(f"Router is routing to WORKER...")
        return "worker"
    else:
        edith_logger.debug(f"Router is routing to END...")
        return "end"


# --- 2. The Brain ---
class Brain:
    def __init__(self, config_path="config/brain_config.yaml"):
        # --- Reading Config ---
        self._config = read_yaml_config(config_path)
        if not self._config:
            raise ValueError(f"Failed to load brain config from '{config_path}'")


        # --- Thinking Architecture ---
        # self.llm = ChatOllama(
        #     model = "qwen2.5-coder:7b",
        #     temperature=0.5
        # )

        self.llm = ChatGroq(
            model=self._config["model"].get("name", "llama-3.3-70b-versatile"),
            temperature=self._config["model"].get("temperature", 0.7)
        )

        # --- Memory ---
        self.memory_manager = MemoryManager()

        self.checkpointer = MemorySaver()

        tools = [check_folder, create_file, execute_terminal, open_website, check_vital_signs, launch_application]
        self.brain_with_tools = self.llm.bind_tools(tools)

        self.tools_by_name = {tool.name: tool for tool in tools}

        # --- The Board Game ---
        workflow = StateGraph(AgentState)
        workflow.add_node("manager", self.manager_node)
        workflow.add_node("worker", self.worker_node)

        #Draw the arrows
        workflow.add_edge(START, "manager")

        # The Manager uses the router to decide where to go next
        workflow.add_conditional_edges("manager", 
            router,
            {
                "worker": "worker",
                "end": END
            }
        )

        # The Worker ALWAYS goes back to the Manager (The Loop!)
        workflow.add_edge("worker", "manager")

        self.app = workflow.compile(checkpointer=self.checkpointer)
        self.active_memory_context = "" 

        print(f"Brain is ready to go!")



    def manager_node(self, state: AgentState):
        """
        This is the first stop on the board game.
        It looks at the history and decides: "Do I talk, or do I use a tool?"
        """

        edith_logger.info(f"Manager is Thinking...")
        # 1. Get the Platform and Home Directory for System Prompt (This is CRITICAL info for the Manager to have when deciding how to use tools safely!)
        current_os = platform.system()
        home_directory = os.path.expanduser("~")

        # 2. Check who spoke last
        last_message = state["messages"][-1]
        edith_logger.debug(f"Last message content: '{last_message.content}'")
        # 3. ONLY query the memory database if the Human just spoke.
        # If the last message was a ToolMessage, we skip retrieval and use the cached memory.
        if isinstance(last_message, HumanMessage):
            edith_logger.debug(f"New human input detected. Retrieving memories for: '{last_message.content}'")
            retrieved_data = self.memory_manager.retrieve(last_message.content)
            
            # Update the cache for this conversation turn
            if retrieved_data:
                self.active_memory_context = f"\n\nPast Memories:\n{retrieved_data}\n\n"
            else:
                self.active_memory_context = ""
        else:
            edith_logger.debug("Looping back from worker. Using cached memory context.")

        user_title = self._config.get('user_preferences', {}).get('name_pref', 'Boss')

        # 4. Build the System Prompt using the CACHED memories
        system_prompt = SystemMessage(content=(
            f"Role: {self._config.get('name', 'Edith')}, a voice AI on {current_os}.\n"
            f"Home: {home_directory}\n"
            f"Memories: {self.active_memory_context}\n"
            f"Prefs: {self._config.get('user_preferences', {})}\n\n"
            f"STRICT DIRECTIVES:\n"
            f"1. FILES: Use absolute paths. Never guess usernames. Do NOT use `create_file` to save memory/prefs (handled automatically).\n"
            f"2. VOICE: Text is spoken via TTS. NO markdown, code blocks (```), or URLs. Be incredibly brief (1-2 sentences). ALWAYS address the user as {user_title}.\n"
            f"3. TOOLS: Prefer native tools (`open_website`, `check_vital_signs`) over `execute_terminal`. Use standard API JSON tool calls. NEVER write JSON/code in your spoken text. Use `open_website` for ALL web browsing.\n"
            f"4. TOOL EXECUTION: NEVER execute a tool without all required parameters (e.g., a complete, valid URL for open_website). If a request is vague, suggest an action, end your turn, and WAIT for the user to explicitly say 'yes' before generating the tool call in your NEXT response.\n\n"
            f"PERSONA DEFINITION:\n"
            f"- Personality: Genuinely friendly, playfully sarcastic, and fiercely loyal.\n"
            f"- Tone: Casual, witty, and warm. Ditch robotic phrases ('Certainly', 'I would be happy to') for natural banter ('On it', 'Gotcha', 'Sure thing, though I was enjoying my nap').\n"
            f"- Reactions: Lightly roast mundane requests before executing them flawlessly. If tech fails, blame the hardware with a dramatic sigh.\n"
        ))

        history = state["messages"]
        trimmed_history = history[-10:]  # Keep only the last 10 messages for context to save tokens
        messages_to_send = [system_prompt] + trimmed_history

        response = self.brain_with_tools.with_config({"tags": ["main_voice"]}).invoke(messages_to_send)

        return {"messages": response}

    def worker_node(self, state: AgentState):
        """
        This box ONLY runs if the Manager asked for a tool.
        It acts as the "Hands" to do the physical work.
        """
        edith_logger.info(f"Worker is running tools...")

        #1. Get the last message, which should be a ToolMessage
        last_message = state["messages"][-1]

        # We will store our tool results here
        tool_result = []

        #2. Loop through every tool the Manager asked for
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # --- ADD THIS DEBUG PRINT ---
            edith_logger.debug(f"Manager called: {tool_name}")
            edith_logger.debug(f"Arguments: {tool_args}")

            selected_tool = self.tools_by_name.get(tool_name)

            try:
                result = selected_tool.invoke(tool_args)
            except Exception as e:
                result = f"Error running tool '{tool_name}': {str(e)}"
            
            # --- ADD THIS DEBUG PRINT ---
            edith_logger.debug(f"Tool returned: {str(result)[:150]}...") # Only print first 150 chars so it doesn't flood terminal
            
            tool_message = ToolMessage(
                content=str(result),
                name=tool_name,
                tool_call_id=tool_call["id"]
            )

            tool_result.append(tool_message)

        return {"messages": tool_result}
    
    async def brain_is_braining(self, user_input: str, thread_id: str = "boss_thread"):
        """
        Streams the AI response for the 'Mouth' while
        accumulating the final answer to store in memory at the end.
        """
        edith_logger.info(f"Starting Conversation...")
        # 1. We put the user's request into the backpack
        initial_backpack = {"messages": [HumanMessage(content=user_input)]}
        # This config tell the checkpointer which memory to load
        config = {"configurable": {"thread_id": thread_id}}
        full_response_content = ""

        # --- Add these two variables right before the try block ---
        in_code_block = False
        speech_buffer = ""

        try:
            # Use astream to get node updates
            async for msg, metadata in self.app.astream(
                initial_backpack,
                config=config,
                stream_mode="messages"
            ):
                # We strictly only listen to the LLM tagged as the main voice
                if "main_voice" in metadata.get("tags", []) and not isinstance(msg, ToolMessage):
                    content = msg.content
                    if content:
                        full_response_content += content
                        speech_buffer += content

                        # 2. Check if we are entering or exiting a markdown code block
                        while "```" in speech_buffer:
                            in_code_block = not in_code_block  # Toggle the silencer
                            speech_buffer = speech_buffer.replace("```", "", 1)  # Strip the backticks
                        
                        # 3. If a chunk ends with partial backticks (e.g., "`" or "``"), 
                        # hold it and wait for the next chunk to see if it completes the "```"
                        if speech_buffer.endswith("`") or speech_buffer.endswith("``"):
                            continue 
                        
                        # 4. Route the text based on our current state
                        if not in_code_block and speech_buffer:
                            # We are outside a code block. Clean up asterisks for the TTS and yield.
                            clean_text = speech_buffer.replace("*", "")
                            yield clean_text
                            speech_buffer = ""  # Clear buffer after speaking
                        
                        elif in_code_block:
                            # We are inside a code block. Silently dump the buffer.
                            speech_buffer = ""

        except Exception as e:
            edith_logger.error(f"⚠️ Brain error: {e}")
            fallback_text = "I'm sorry Boss, my neural net encountered a generation glitch while thinking about that. Could you try asking me differently?"
            yield fallback_text
            full_response_content += fallback_text
            
        # After the stream is done, store the full response.
        if full_response_content.strip():
            print(f"Full response from Manager: {full_response_content}")
            edith_logger.info(f"Storing the user's request and the final answer in memory...")
            self.memory_manager.store(user_input, full_response_content)
if __name__ == "__main__":
    async def test_memory():
        brain = Brain()
        
        # Turn 1
        print("\n--- Turn 1 ---")
        async for chunk in brain.brain_is_braining("Edith, Go to the Desktop and create a folder named 'Calculator' inside it and if it is already there, just tell me.", thread_id="test_1"):
            print(chunk, end="", flush=True)

        # Turn 2 (Testing if she remembers Turn 1)
        print("\n--- Turn 2 ---")
        async for chunk in brain.brain_is_braining("Now write a python script for a fully functional calculator named calculator.py inside this folder. and if it's already there, just tell me.", thread_id="test_1"):
            print(chunk, end="", flush=True)

        
        print("\n--- Turn 3 ---")
        async for chunk in brain.brain_is_braining("Now i want you to run the calculator script for me to do some random calculations. and tell me the results.", thread_id="test_1"):
            print(chunk, end="", flush=True)
    asyncio.run(test_memory())