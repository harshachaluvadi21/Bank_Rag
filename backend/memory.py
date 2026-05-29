class RAGMemory:
    """
    Manages chatbot conversation history using a clean, native, and robust Python list.
    This maintains past dialogue context, allowing the Query Rewriter to understand 
    contextual pronouns like 'its advantages' or 'their timings'.
    
    Why this approach is excellent:
    1. Future-proof: Modern LangChain versions have deprecated the legacy 'langchain.memory' 
       package. A native implementation avoids deprecation errors and is highly robust!
    2. Transparent: Extremely beginner-friendly, showing students exactly how dialogue 
       history is collected, formatted, and preserved.
    """
    def __init__(self):
        # List of dictionaries, each holding 'input' (user query) and 'output' (LLM response)
        self.history = []
        
    def get_history(self) -> str:
        """
        Retrieves the conversation history formatted as a single, clean transcript string.
        
        Returns:
            str: A formatted transcript (e.g., "Human: ... \nAI: ...") or an empty string.
        """
        if not self.history:
            return ""
            
        history_lines = []
        for turn in self.history:
            history_lines.append(f"Human: {turn['input']}")
            history_lines.append(f"AI: {turn['output']}")
        return "\n".join(history_lines)
        
    def save_interaction(self, user_query: str, bot_response: str):
        """
        Saves a single round of interaction (user question + bot answer) into history.
        
        Parameters:
            user_query (str): The exact question typed by the user.
            bot_response (str): The final generated answer from the AI.
        """
        self.history.append({
            "input": user_query,
            "output": bot_response
        })
        
    def clear_memory(self):
        """
        Clears the stored memory transcript.
        """
        self.history = []
