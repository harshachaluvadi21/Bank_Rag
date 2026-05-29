import os
import sys

def initialize_llm():
    """
    Reads LLM_PROVIDER from environment and instantiates the chosen LLM with a 0 temperature
    for extreme factual precision and deterministic outputs.
    
    Supports:
        - Groq (llama-3.1-8b-instant) [Recommended for Speed]
        - Gemini (gemini-2.5-flash) [Recommended for Context size]
        - OpenAI (gpt-4o-mini) [Industry standard]
        
    Returns:
        BaseChatModel: An initialized LangChain chat model wrapper.
    """
    # 1. Read configuration
    provider = os.getenv("LLM_PROVIDER", "groq").lower().strip()
    
    # Color helper codes
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    
    # 2. Check and initialize based on provider
    if provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or "your_groq_api_key" in groq_key or len(groq_key.strip()) < 10:
            print(f"{RED}[ERROR] GROQ_API_KEY is missing or invalid in your .env file.{RESET}")
            print(f"{YELLOW}Please obtain a free key from https://console.groq.com/ and update your '.env' file.{RESET}")
            sys.exit(1)
            
        print("\033[94m[llm] Initializing ChatGroq (model: 'llama-3.1-8b-instant')...\033[0m")
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0.0,
                api_key=groq_key
            )
            return llm
        except Exception as e:
            print(f"{RED}[ERROR] Failed to initialize ChatGroq: {e}{RESET}")
            sys.exit(1)
            
    elif provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or "your_gemini_api_key" in gemini_key or len(gemini_key.strip()) < 10:
            print(f"{RED}[ERROR] GEMINI_API_KEY is missing or invalid in your .env file.{RESET}")
            print(f"{YELLOW}Please obtain a free key from https://aistudio.google.com/ and update your '.env' file.{RESET}")
            sys.exit(1)
            
        print("\033[94m[llm] Initializing ChatGoogleGenerativeAI (model: 'gemini-2.5-flash')...\033[0m")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.0,
                google_api_key=gemini_key
            )
            return llm
        except Exception as e:
            print(f"{RED}[ERROR] Failed to initialize ChatGoogleGenerativeAI: {e}{RESET}")
            sys.exit(1)
            
    elif provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or "your_openai_api_key" in openai_key or len(openai_key.strip()) < 10:
            print(f"{RED}[ERROR] OPENAI_API_KEY is missing or invalid in your .env file.{RESET}")
            print(f"{YELLOW}Please obtain a key from https://platform.openai.com/ and update your '.env' file.{RESET}")
            sys.exit(1)
            
        print("\033[94m[llm] Initializing ChatOpenAI (model: 'gpt-4o-mini')...\033[0m")
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=openai_key
            )
            return llm
        except Exception as e:
            print(f"{RED}[ERROR] Failed to initialize ChatOpenAI: {e}{RESET}")
            sys.exit(1)
            
    else:
        print(f"{RED}[ERROR] Invalid LLM_PROVIDER '{provider}' specified in '.env'!{RESET}")
        print(f"{YELLOW}Supported options are: 'groq', 'gemini', or 'openai'.{RESET}")
        sys.exit(1)
