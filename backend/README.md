# BankRAG Backend Engine

The backend handles the core Adaptive RAG pipeline and exposes it via a FastAPI wrapper.

## Architecture Highlights
- **Document Loading & Splitting (`loader.py`):** Ingests raw `.txt` files into manageable chunks with metadata.
- **Embeddings & Retrieval (`embeddings.py`, `retriever.py`):** Uses SentenceTransformers for local embedding, BM25 for sparse retrieval, and ChromaDB for dense vector search.
- **Dynamic Routing (`router.py`):** Decomposes queries, detects freshness intent, and identifies the banking domain scope.
- **Adaptive LLM Generation (`llm.py`, `prompt.py`):** Powered by Groq/Llama-3.1 to generate answers based on contextual confidence.
- **FastAPI Wrapper (`api.py`):** Exposes `/api/health` and `/api/chat` for seamless Next.js frontend integration.

## Setup
1. Create a virtual environment and `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and fill in `GROQ_API_KEY`.
3. Put banking text documents in `backend/data/`.
4. Run the server: `python -m uvicorn api:app --host 127.0.0.1 --port 8000`
