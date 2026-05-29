# BankRAG Frontend Interface

A premium Next.js 15 interface designed to visualize the internal mechanics of the Adaptive RAG pipeline.

## Features
- **Dark Theme & Glassmorphism:** A modern, banking-focused aesthetic.
- **Framer Motion Animations:** Smooth transitions and UI interactions.
- **Live Analytics Panel:** Real-time metadata including query routing strategy, fallback detection, latency, and chunk counts.
- **Source Preview Drawer:** Inspect retrieved chunk metadata, BM25/Vector relevance scores, and file origins in a side drawer.

## Setup
1. `npm install`
2. Copy `.env.example` to `.env` (ensure `NEXT_PUBLIC_API_URL` points to the FastAPI backend).
3. Run the development server: `npm run dev`
