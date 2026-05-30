import sys
import os
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

def get_embeddings_model():
    """
    Initializes and returns the FastEmbed Embeddings model.
    This model uses ONNX Runtime and requires virtually no memory, 
    making it perfect for Render's 512MB free tier while bypassing Google API limits!
    
    Returns:
        FastEmbedEmbeddings: The initialized embeddings model.
    """
    print("\033[94m[embeddings] Loading FastEmbed (Low-Memory) Model...\033[0m")
    
    try:
        embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        print("\033[92m[OK] FastEmbed Model loaded successfully!\033[0m")
        return embeddings
    except Exception as e:
        print(f"\033[91m[ERROR] Could not load the FastEmbed model: {e}\033[0m")
        sys.exit(1)
