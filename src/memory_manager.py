from src.memory_store import MemoryStore
from src.memory_supervisor import MemorySupervisor
from utils.logger import edith_logger

class MemoryManager:
    """
    Manages the storage and retrieval of conversation history/memories.
    Acts as the bridge between the LLM Engine and the Vector Database.
    """
    def __init__(self):
        self.store_db = MemoryStore()
        self.supervisor = MemorySupervisor()

    def store(self, user_msg: str, ai_msg: str):
        """
        Saves the interaction to the memory store.
        Format: "User: [msg] | AI: [msg]"
        """
        # We save the pair so the context is preserved.
        memory = self.supervisor.extract(user_msg, ai_msg)

        if memory == "NONE":
            edith_logger.info("🚫 No permanent memory extracted.")
            return

        try:
            self.store_db.add_memory(memory)
            edith_logger.info(f"💾 Memory saved: {memory}")
        except Exception as e:
            edith_logger.warning(f"⚠️ Failed to save memory: {e}")

    def retrieve(self, query: str) -> str:
        """
        Retrieves relevant memories based on the query.
        Returns a formatted string to be injected into the system prompt.
        """
        try:
            should_retrieve = self.supervisor.should_retrieve(query)
            if should_retrieve.lower() == "no":
                edith_logger.info(f"🚫 Memory retrieval deemed unnecessary by supervisor: {should_retrieve}")
                return ""
            else:
                edith_logger.info(f"✅ Memory retrieval approved by supervisor: {should_retrieve}")
                results = self.store_db.search_memory(query, n_results=3)
            if not results:
                edith_logger.info("📭 No relevant memories found.")
                return ""
            
            # Format results for the LLM
            formatted_memories = "\n".join([f"- {m}" for m in results])
            return formatted_memories
        except Exception as e:
            edith_logger.warning(f"⚠️ Failed to retrieve memory: {e}")
            return ""

if __name__ == "__main__":
    # Test
    mm = MemoryManager()
    mm.retrieve("test")
