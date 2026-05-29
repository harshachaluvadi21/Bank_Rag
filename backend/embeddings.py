import sys
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    """
    Initializes and returns the HuggingFace local embeddings model ('all-MiniLM-L6-v2').
    This model runs completely locally on CPU, making it cost-free, fast, and private!
    
    Returns:
        HuggingFaceEmbeddings: The initialized embeddings model.
    """
    print("\033[94m[embeddings] Loading HuggingFace Embedding Model ('all-MiniLM-L6-v2')...\033[0m")
    
    try:
        # Load local embeddings model using Hugging Face
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        print("\033[92m[OK] Local Embeddings Model loaded successfully!\033[0m")
        return embeddings
    except Exception as e:
        print(f"\033[91m[ERROR] Could not load the local embedding model: {e}\033[0m")
        print("\033[93mEnsure internet connection is active on first run to download the model (~90MB).\033[0m")
        sys.exit(1)
