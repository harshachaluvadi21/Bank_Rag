import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from prompt import QUERY_REWRITE_PROMPT

load_dotenv()
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.0,
    max_tokens=100
)

chat_history = """Assistant: Hello! I am BankRAG, your specialized banking assistant. How can I help you today?
User: What is an NPA in banking?
Assistant: The underwriting phase ensures that banks only lend to individuals who have the proven capacity to repay, thereby maintaining a low rate of Non-Performing Assets (NPAs)."""

query = "How does it affect a bank's profitability?"

formatted = QUERY_REWRITE_PROMPT.format(chat_history=chat_history, latest_question=query)
print("PROMPT:")
print(formatted)
print("-" * 50)
try:
    resp = llm.invoke(formatted)
    print("OUTPUT:")
    print(resp.content)
except Exception as e:
    print("Error:", e)
