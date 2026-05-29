# BankRAG: Next-Gen Adaptive RAG for Banking 🏦

BankRAG is a state-of-the-art modular Adaptive Retrieval-Augmented Generation (RAG) system specialized in the Banking and Financial Services domain.

## Overview

Unlike standard naive RAG systems, BankRAG employs:
- **Dynamic Query Routing:** Assesses query complexity and intent before deciding to use Vector Search, BM25 Keyword Search, or a Hybrid approach.
- **Cross-Encoder Reranking:** Ensures that the retrieved context is highly relevant to the query.
- **Banking Domain Detection:** Acts as a guardrail to gracefully handle out-of-domain (OOD) questions.
- **Query Decomposition:** Breaks down complex, multi-part questions into individual semantic searches.
- **Confidence-Based Fallback:** Automatically expands queries and retries if the retrieval confidence falls below a configured threshold.

## Repository Structure

- `backend/`: FastAPI wrapper and Core Python RAG pipeline (LangChain, ChromaDB, Groq, SentenceTransformers).
- `frontend/`: Next.js 15, Shadcn UI, Framer Motion interface with Analytics Dashboard.
- `docs/`: Architectural diagrams, API specifications, and interview preparation materials.
- `assets/`: Demo videos, logos, and UI screenshots.

## Quick Start

1. Start Backend:
```bash
cd backend
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

2. Start Frontend:
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to interact with BankRAG!
