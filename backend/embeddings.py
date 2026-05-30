import sys
import os
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    """
    Initializes and returns the HuggingFace Embeddings model.
    Using this local, open-source model avoids API quota limits!
    
    Returns:
        HuggingFaceEmbeddings: The initialized embeddings model.
    """
    print("\033[94m[embeddings] Loading HuggingFace Embeddings Model...\033[0m")
    
    try:
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        print(f"\033[92m[OK] HuggingFace Embeddings Model ({model_name}) loaded successfully!\033[0m")
        return embeddings
    except Exception as e:
        print(f"\033[91m[ERROR] Could not load the HuggingFace embedding model: {e}\033[0m")
        sys.exit(1)
