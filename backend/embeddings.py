import sys
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embeddings_model():
    """
    Initializes and returns the Google Gemini Embeddings model.
    This uses an API, shifting the memory load away from the server,
    which is perfect for Render's free tier.
    
    Returns:
        GoogleGenerativeAIEmbeddings: The initialized embeddings model.
    """
    print("\033[94m[embeddings] Loading Google Gemini Embeddings Model...\033[0m")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\033[91m[ERROR] GOOGLE_API_KEY environment variable is missing!\033[0m")
        print("\033[93mPlease add your Google API Key to the environment variables on Render.\033[0m")
        sys.exit(1)
        
    try:
        # Load Google embeddings model
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )
        print("\033[92m[OK] Google Embeddings Model loaded successfully!\033[0m")
        return embeddings
    except Exception as e:
        print(f"\033[91m[ERROR] Could not load the Google embedding model: {e}\033[0m")
        sys.exit(1)
