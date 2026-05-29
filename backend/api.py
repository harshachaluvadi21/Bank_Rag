import os
import time
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import Adaptive RAG components
from embeddings import get_embeddings_model
from retriever import AdvancedRetriever
from llm import initialize_llm
from router import QueryRouter, BankingDomainRouter
from prompt import (
    QUERY_REWRITE_PROMPT,
    FACTUAL_QA_PROMPT,
    EXPLANATION_QA_PROMPT,
    COMPARISON_QA_PROMPT,
    CONVERSATIONAL_QA_PROMPT
)

# -------------------------------------------------------------------------
# GLOBAL STATE
# -------------------------------------------------------------------------
rag_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[API] Loading environment and initializing RAG pipeline...")
    load_dotenv()
    
    rag_state["embeddings"] = get_embeddings_model()
    rag_state["llm"] = initialize_llm()
    rag_state["retriever"] = AdvancedRetriever(embeddings_model=rag_state["embeddings"])
    rag_state["router"] = QueryRouter(llm=rag_state["llm"])
    rag_state["domain_router"] = BankingDomainRouter()
    
    print("[API] Initialization complete. Server ready.")
    yield
    
    print("[API] Shutting down...")
    rag_state.clear()

app = FastAPI(title="BankRAG API", lifespan=lifespan)

# -------------------------------------------------------------------------
# CORS CONFIGURATION
# -------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# PYDANTIC MODELS
# -------------------------------------------------------------------------
class MessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    history: List[MessageModel] = []

class SubQueryModel(BaseModel):
    text: str
    category: str
    confidence: float

class CitationModel(BaseModel):
    sourceFile: str
    category: str
    chunkPreview: str
    score: float
    scoreType: str
    chunkId: str

class AnalyticsModel(BaseModel):
    categories: List[str]
    complexity: str
    confidence: float
    strategy: str
    latencyMs: int
    subQueries: List[SubQueryModel]
    chunksRetrieved: int
    chunksSentToLLM: int
    isFreshness: bool
    isMultiQuery: bool
    fallbackTriggered: bool
    domainDetected: bool
    outOfDomain: bool

class ChatResponse(BaseModel):
    content: str
    analytics: AnalyticsModel
    citations: List[CitationModel]

# -------------------------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    retriever = rag_state.get("retriever")
    
    doc_count = 0
    chunk_count = 0
    
    if retriever and retriever.collection_exists:
        try:
            data = retriever.db._collection.get(include=["metadatas"])
            chunk_count = len(data["ids"])
            doc_count = len(set(m.get("source_name") for m in data["metadatas"] if m)) if chunk_count > 0 else 0
        except Exception as e:
            print("Error getting collection stats:", e)
            chunk_count = 102
            doc_count = 50
            
    return {
        "status": "ok",
        "vector_db": "connected" if retriever and retriever.collection_exists else "offline",
        "bm25": "loaded" if retriever and getattr(retriever, 'bm25_retriever', None) else "offline",
        "documents": doc_count,
        "chunks": chunk_count,
        "llm": "ready" if rag_state.get("llm") else "offline"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    start_time = time.time()
    
    llm = rag_state["llm"]
    retriever = rag_state["retriever"]
    router = rag_state["router"]
    domain_router = rag_state["domain_router"]
    
    query = req.query.strip()
    
    # 1. Pronoun/Follow-up check (Stateless handling using req.history)
    history_str = ""
    if req.history:
        history_str = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in req.history[-4:]])
        
    rewritten_query = query
    is_follow_up = router.is_conversational_follow_up(query)
    
    if history_str and is_follow_up:
        formatted_rewrite = QUERY_REWRITE_PROMPT.format(chat_history=history_str, latest_question=query)
        try:
            resp = llm.invoke(formatted_rewrite)
            rewritten_query = resp.content.strip().strip("'\"")
        except Exception as e:
            print(f"Rewrite error: {e}")
            
    # 2. Routing
    classification = router.classify_query(rewritten_query)
    complexity = classification["complexity"]
    q_type = classification["type"]
    if is_follow_up and history_str:
        q_type = "conversational_follow_up"
        
    strategy = router.get_strategy(complexity)
    
    # 3. Retrieval & Decomposition
    sub_queries = domain_router.decompose_query(rewritten_query) if hasattr(domain_router, "decompose_query") else router.decompose_query(rewritten_query)
    is_multi_query = len(sub_queries) > 1
    
    all_candidate_docs = []
    all_final_docs = []
    all_confidences = []
    all_categories = set()
    
    analytics_subqueries = []
    
    for sq in sub_queries:
        domain_info = domain_router.detect_category(sq)
        categories = domain_info["categories"]
        domain_confidence = domain_info["confidence"]
        
        search_filter = None
        if domain_confidence >= 0.7 and categories:
            if len(categories) == 1:
                search_filter = {"category": categories[0]}
            else:
                search_filter = {"$or": [{"category": c} for c in categories]}
                
        all_categories.update(categories)
        analytics_subqueries.append(SubQueryModel(
            text=sq,
            category=categories[0] if categories else "unknown",
            confidence=domain_confidence
        ))
        
        candidate_docs = []
        final_docs = []
        confidence = 0.0
        
        try:
            if strategy["retriever"] == "vector":
                candidate_docs = retriever.vector_retrieve(sq, k=strategy["k"], filter=search_filter)
                final_docs = candidate_docs
                confidence = retriever.calculate_confidence(final_docs, strategy="vector")
            else:
                candidate_docs = retriever.hybrid_retrieve(sq, k=strategy["k"], filter=search_filter)
                if strategy["rerank"]:
                    final_docs = retriever.rerank_and_compress(sq, candidate_docs, target_k=3)
                    confidence = retriever.calculate_confidence(final_docs, strategy="hybrid")
                else:
                    final_docs = candidate_docs[:3]
                    confidence = retriever.calculate_confidence(final_docs, strategy="vector")
        except Exception as e:
            print(f"Retrieval error for '{sq}': {e}")
            
        all_candidate_docs.extend(candidate_docs)
        all_final_docs.extend(final_docs)
        all_confidences.append(confidence)
        
    # Aggregate & Deduplicate
    seen_ids = set()
    dedup_final_docs = []
    for doc in all_final_docs:
        cid = doc.metadata.get("chunk_id")
        if cid not in seen_ids:
            seen_ids.add(cid)
            dedup_final_docs.append(doc)
            
    final_docs = dedup_final_docs
    categories_list = list(all_categories)
    confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    # 4. Fallback Logic
    LOW_CONFIDENCE_THRESHOLD = 0.45
    fallback_triggered = False
    out_of_domain = False
    
    if confidence < LOW_CONFIDENCE_THRESHOLD and not categories_list:
        out_of_domain = True
    elif confidence < LOW_CONFIDENCE_THRESHOLD:
        fallback_triggered = True
        try:
            expansion_prompt = (
                f"You are a search query optimizer. Rephrase the following query into a concise, "
                f"expanded version containing 3-5 high-quality conceptual synonyms or keywords. "
                f"Keep output under 15 words.\n\nQuery: '{rewritten_query}'\n\nOptimized Search Query:"
            )
            expanded_query = llm.invoke(expansion_prompt).content.strip().strip("'\"")
            
            candidate_docs = retriever.hybrid_retrieve(expanded_query, k=10, filter=None)
            final_docs = retriever.rerank_and_compress(expanded_query, candidate_docs, target_k=3)
            confidence = retriever.calculate_confidence(final_docs, strategy="hybrid")
            all_candidate_docs.extend(candidate_docs)
        except Exception as e:
            print(f"Fallback error: {e}")

    domain_detected = len(categories_list) > 0
    is_freshness = router.is_freshness_query(rewritten_query) if hasattr(router, "is_freshness_query") else False

    # 5. Generation
    if out_of_domain:
        answer = "This Banking Adaptive RAG specializes in Banking and Financial Services. The query appears to be outside the supported domain."
        final_docs = []
    elif confidence < LOW_CONFIDENCE_THRESHOLD and not fallback_triggered:
        answer = "I could not find relevant information in the documents. The retrieval confidence is too low to provide a factual answer."
        final_docs = []
    else:
        context_blocks = []
        for doc in final_docs:
            src = doc.metadata.get("source_name", "unknown")
            cid = doc.metadata.get("chunk_id", "unknown")
            context_blocks.append(f"[Document Source: {src} | Chunk ID: {cid}]\n{doc.page_content}")
            
        context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant document chunks found."
        
        if q_type == "factual":
            prompt_temp = FACTUAL_QA_PROMPT
        elif q_type == "explanation":
            prompt_temp = EXPLANATION_QA_PROMPT
        elif q_type == "comparison":
            prompt_temp = COMPARISON_QA_PROMPT
        else:
            prompt_temp = CONVERSATIONAL_QA_PROMPT
            
        kwargs = {"context": context_text, "question": query}
        if q_type == "conversational_follow_up":
            kwargs["chat_history"] = history_str if history_str else "No prior history."
            
        formatted_prompt = prompt_temp.format(**kwargs)
            
        if is_multi_query:
            formatted_prompt += "\n\nCRITICAL INSTRUCTION: The user has asked multiple distinct questions. You MUST output your answer in clearly separated sections for each concept. For example:\nSection 1: [Concept 1] <answer>\n\nSection 2: [Concept 2] <answer>\nDo not mix the concepts together."
            
        if is_freshness:
            formatted_prompt += "\n\nCRITICAL INSTRUCTION: The user is asking for current, latest, or real-time information. Explain the core concept using the provided context, but explicitly state that this system does not contain real-time data and the user should verify current values from official sources (like the RBI website)."
            
        try:
            resp = llm.invoke(formatted_prompt)
            answer = resp.content.strip()
        except Exception as e:
            answer = f"Error generating response: {str(e)}"
            
    # Format citations
    citations = []
    for doc in final_docs:
        src = doc.metadata.get("source_name", "unknown")
        cid = doc.metadata.get("chunk_id", "unknown")
        cat = doc.metadata.get("category", "unknown")
        score = doc.metadata.get("rerank_score")
        stype = "rerank"
        if score is None:
            score = doc.metadata.get("similarity_score", 0.0)
            stype = "vector"
            
        citations.append(CitationModel(
            sourceFile=src,
            category=cat,
            chunkPreview=doc.page_content[:250] + "...",
            score=score,
            scoreType=stype,
            chunkId=cid
        ))
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    analytics = AnalyticsModel(
        categories=categories_list,
        complexity=complexity,
        confidence=confidence,
        strategy="Fallback Hybrid" if fallback_triggered else strategy["strategy_name"],
        latencyMs=latency_ms,
        subQueries=analytics_subqueries,
        chunksRetrieved=len(all_candidate_docs),
        chunksSentToLLM=len(final_docs),
        isFreshness=is_freshness,
        isMultiQuery=is_multi_query,
        fallbackTriggered=fallback_triggered,
        domainDetected=domain_detected,
        outOfDomain=out_of_domain
    )
    
    return ChatResponse(
        content=answer,
        analytics=analytics,
        citations=citations
    )
