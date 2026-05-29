import os
import sys
import time
from dotenv import load_dotenv

# Ensure Windows console supports UTF-8 character encoding for premium box-drawing characters
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Enable native ANSI support on Windows Command Prompt if needed
os.system('')

# Terminal colors for a premium, engaging console interface
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Print a stylish ASCII Art Header for the Adaptive RAG chatbot
print(f"{CYAN}{BOLD}")
print(r"    ___         __                 __     _             ____  ___   ______")
print(r"   /   |  _____/ /_____  __  _____/ /_   | |     /|    / __ \/   | / ____/")
print(r"  / /| | / __  / __/ __ \/ / / / ___/ __ \  | |   /  |  / /_/ / /| |/ / __  ")
print(r" / ___ |/ /_/ / /_/ /_/ / /_/ / /__/ / / /   | | / /| |/ _, _/ ___ / /_/ /  ")
print(r"/_/  |_|\__,_/\__/\____/\__,_/\___/_/ /_/     |__/_/ |_/_/ |_/_/  |_\____/   ")
print(r"                                                                            ")
print(f"       ~ A State-of-the-Art, Modular Adaptive RAG Chatbot ~         {RESET}\n")

# -------------------------------------------------------------------------
# STEP 1: LOAD ENVIRONMENT VARIABLES
# -------------------------------------------------------------------------
print(f"{BLUE}[i] Loading environment variables from .env...{RESET}")
load_dotenv()

# -------------------------------------------------------------------------
# STEP 2: IMPORT MODULAR ADAPTIVE RAG LIBRARIES
# -------------------------------------------------------------------------
print(f"{BLUE}[i] Initializing Adaptive RAG modules...{RESET}")
try:
    from loader import load_and_split_documents
    from embeddings import get_embeddings_model
    from retriever import AdvancedRetriever
    from llm import initialize_llm
    from memory import RAGMemory
    from router import QueryRouter, BankingDomainRouter
    from analytics import RAGAnalytics
    from prompt import (
        QUERY_REWRITE_PROMPT,
        FACTUAL_QA_PROMPT,
        EXPLANATION_QA_PROMPT,
        COMPARISON_QA_PROMPT,
        CONVERSATIONAL_QA_PROMPT
    )
except ImportError as e:
    print(f"{RED}[ERROR] Failed to import project modules or dependencies.{RESET}")
    print(f"{YELLOW}Did you install requirements? Run: pip install -r requirements.txt{RESET}")
    print(f"{YELLOW}Error details: {e}{RESET}")
    sys.exit(1)

# -------------------------------------------------------------------------
# STEP 3: INITIALIZE CORE COMPONENTS
# -------------------------------------------------------------------------
# 1. Initialize local embeddings
embeddings = get_embeddings_model()

# 2. Initialize and validate the LLM (supports Groq, Gemini, OpenAI)
llm = initialize_llm()

# Check for --reset command-line flag to wipe and re-index the collection
reset_db = "--reset" in sys.argv or "-r" in sys.argv

# 3. Initialize Advanced Retriever (Chroma DB Cloud Connection)
retriever = AdvancedRetriever(embeddings_model=embeddings)

# Check if reset flag is passed to wipe and re-index the collection
if reset_db:
    retriever.reset_collection()

# 4. Handle cold start / indexing if collection doesn't exist
if not retriever.collection_exists:
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = str(BASE_DIR / "data")
    print(f"{YELLOW}[i] Beginning indexing pipeline...{RESET}")
    
    # Load and split documents
    chunks = load_and_split_documents(data_dir=DATA_DIR, chunk_size=2500, chunk_overlap=250)
    
    if not chunks:
        print(f"{RED}[ERROR] No document chunks could be created. Cannot initialize chatbot.{RESET}")
        sys.exit(1)
        
    # Write documents to Chroma DB and sync local BM25
    retriever.initialize_with_documents(chunks)

# 5. Initialize Conversation Memory
chat_memory = RAGMemory()

# 6. Initialize Query Router
router = QueryRouter(llm=llm)

# 7. Initialize Banking Domain Router
domain_router = BankingDomainRouter()

# Print LangSmith observability status if enabled
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    print(f"{GREEN}[OK] LangSmith Tracing is ACTIVE! Traces are streaming to: {BOLD}{os.getenv('LANGCHAIN_PROJECT')}{RESET}")

# -------------------------------------------------------------------------
# STEP 4: INTERACTIVE CHAT LOOP
# -------------------------------------------------------------------------
print(f"\n{GREEN}{BOLD}========================================================================")
print("             ADAPTIVE RAG CHATBOT IS READY FOR QUESTIONS!")
print("========================================================================{RESET}")
print(f"Adaptive Features: LLM Routing | Dynamic Retrieval | Confidence retries | Performance Analytics")
print(f"Type {RED}'exit'{RESET} or {RED}'quit'{RESET} to close. Type {YELLOW}'clear'{RESET} to reset chat history.\n")

while True:
    try:
        print(f"{CYAN}{BOLD}Student Question: {RESET}", end="")
        query = input().strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}[i] Exiting program... Goodbye!{RESET}")
        break

    if not query:
        continue

    # Support resetting conversation memory
    if query.lower() == "clear":
        chat_memory.clear_memory()
        print(f"{GREEN}[OK] Conversation memory cleared!{RESET}\n")
        continue

    if query.lower() in ["exit", "quit"]:
        print(f"{YELLOW}[i] Exiting program... Goodbye!{RESET}")
        break

    # Initialize analytics for this specific conversational turn
    analytics = RAGAnalytics()
    analytics.start_stage("total")

    # =========================================================================
    # ADAPTIVE RAG STEP 1: CONVERSATIONAL PRONOUN CHECK & QUERY REWRITING
    # =========================================================================
    history_str = chat_memory.get_history()
    rewritten_query = query
    
    # Check if the query is a conversational follow-up containing pronouns
    is_follow_up = router.is_conversational_follow_up(query)
    
    if history_str and is_follow_up:
        print(f"\n{BLUE}[1] Pronoun/Follow-up detected. Rewriting conversational query...{RESET}")
        analytics.start_stage("rewriting")
        
        formatted_rewrite_prompt = QUERY_REWRITE_PROMPT.format(
            chat_history=history_str,
            latest_question=query
        )
        try:
            # LLM reconstructs a standalone search query
            response = llm.invoke(formatted_rewrite_prompt)
            rewritten_query = response.content.strip().strip("'\"")
            
            # Print rewrites cleanly
            if rewritten_query.lower() != query.lower():
                print(f"    - Original Question: {YELLOW}\"{query}\"{RESET}")
                print(f"    - Standalone Query : {GREEN}{BOLD}\"{rewritten_query}\"{RESET}")
            else:
                print(f"    - Standalone Query remains: \"{rewritten_query}\"")
        except Exception as e:
            print(f"{RED}[WARNING] Query rewriting failed: {e}. Using original question.{RESET}")
            rewritten_query = query
        finally:
            analytics.end_stage("rewriting")
    else:
        # Optimization: Skip rewriting if fresh topic turn
        print(f"\n{BLUE}[1] Fresh/Self-contained query. Skipping Query Rewriting for performance!{RESET}")

    # =========================================================================
    # ADAPTIVE RAG STEP 2: QUERY CLASSIFICATION & DYNAMIC ROUTING
    # =========================================================================
    print(f"\n{BLUE}[2] Classifying query complexity and routing to retrieval strategy...{RESET}")
    analytics.start_stage("routing")
    
    classification = router.classify_query(rewritten_query)
    complexity = classification["complexity"]
    q_type = classification["type"]
    
    # If the raw query was conversational, force type to follow-up for adaptive prompting
    if is_follow_up and history_str:
        q_type = "conversational_follow_up"
        
    strategy = router.get_strategy(complexity)
    
    analytics.record_metric("query_complexity", complexity)
    analytics.record_metric("query_type", q_type)
    analytics.record_metric("strategy_name", strategy["strategy_name"])
    analytics.record_metric("reranking_enabled", strategy["rerank"])
    
    analytics.end_stage("routing")
    
    print(f"    - Routed to: {GREEN}{BOLD}{strategy['strategy_name']}{RESET}")
    print(f"    - Query Type: {CYAN}{q_type}{RESET}")

    # =========================================================================
    # ADAPTIVE RAG STEP 3: DYNAMIC RETRIEVAL & CONDITION RERANKING
    # =========================================================================
    print(f"\n{BLUE}[3] Executing retrieval strategy (k={strategy['k']})...{RESET}")
    analytics.start_stage("retrieval")
    
    # --- Query Decomposition ---
    sub_queries = domain_router.decompose_query(rewritten_query) if hasattr(domain_router, "decompose_query") else router.decompose_query(rewritten_query)
    is_multi_query = len(sub_queries) > 1
    
    analytics.record_metric("decomposed_subqueries", len(sub_queries))
    print(f"    - Decomposed Sub-queries: {CYAN}{len(sub_queries)}{RESET}")
    for i, sq in enumerate(sub_queries):
        print(f"      {i+1}. {sq}")

    all_candidate_docs = []
    all_final_docs = []
    all_confidences = []
    all_categories = set()
    all_filters = []
    
    for sq in sub_queries:
        # --- Banking Domain Category Detection ---
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
        if search_filter:
            all_filters.append(search_filter)
        
        candidate_docs = []
        final_docs = []
        confidence = 0.0
        
        try:
            # A. Execute designated retrieval algorithm
            if strategy["retriever"] == "vector":
                candidate_docs = retriever.vector_retrieve(sq, k=strategy["k"], filter=search_filter)
                final_docs = candidate_docs
                confidence = retriever.calculate_confidence(final_docs, strategy="vector")
            else: # hybrid
                candidate_docs = retriever.hybrid_retrieve(sq, k=strategy["k"], filter=search_filter)
                
                # B. Conditionally apply reranking if enabled
                if strategy["rerank"]:
                    final_docs = retriever.rerank_and_compress(sq, candidate_docs, target_k=3)
                    confidence = retriever.calculate_confidence(final_docs, strategy="hybrid")
                else:
                    final_docs = candidate_docs[:3]
                    confidence = retriever.calculate_confidence(final_docs, strategy="vector")
                    
        except Exception as e:
            print(f"{RED}[ERROR] Retrieval failed for sub-query '{sq}': {e}{RESET}\n")
            continue
            
        all_candidate_docs.extend(candidate_docs)
        all_final_docs.extend(final_docs)
        all_confidences.append(confidence)
        
    analytics.end_stage("retrieval")
    if strategy["rerank"]:
        analytics.end_stage("reranking")

    # Aggregate & Deduplicate
    seen_ids = set()
    dedup_final_docs = []
    for doc in all_final_docs:
        cid = doc.metadata.get("chunk_id")
        if cid not in seen_ids:
            seen_ids.add(cid)
            dedup_final_docs.append(doc)
            
    final_docs = dedup_final_docs
    candidate_docs = all_candidate_docs
    categories = list(all_categories)
    confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    print(f"    - Categories Detected: {CYAN}{categories if categories else 'None'}{RESET}")
    print(f"    - Filter Applied: {CYAN}{all_filters}{RESET}")
    print(f"    - Retrieval Confidence: {confidence*100:.1f}%")
    print(f"    - Total Chunks Retrieved: {len(final_docs)}")

    analytics.record_metric("confidence_score", confidence)
    analytics.record_metric("chunks_retrieved", len(candidate_docs))
    analytics.record_metric("chunks_sent_to_llm", len(final_docs))

    # =========================================================================
    # ADAPTIVE RAG STEP 4: CONFIDENCE-BASED ADAPTATION (FALLBACK RETRY)
    # =========================================================================
    LOW_CONFIDENCE_THRESHOLD = 0.45
    
    # --- Out of Domain Handling ---
    if confidence < LOW_CONFIDENCE_THRESHOLD and not categories:
        print(f"\n{YELLOW}This Banking Adaptive RAG specializes in Banking and Financial Services. The query appears to be outside the supported domain.{RESET}\n")
        continue

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        print(f"\n{RED}{BOLD}[!] LOW RETRIEVAL CONFIDENCE DETECTED ({confidence*100:.1f}% < {LOW_CONFIDENCE_THRESHOLD*100:.0f}%)!{RESET}")
        print(f"{YELLOW}[i] Re-triggering Query Rewriting and retrying with Expanded Hybrid Strategy...{RESET}")
        
        analytics.record_metric("retry_triggered", True)
        analytics.record_metric("retry_count", 1)
        
        # 1. Expand search query by re-writing with LLM synonym expansion
        analytics.start_stage("rewriting")
        expansion_prompt = (
            f"You are a search query optimizer. Rephrase the following query into a concise, "
            f"expanded version containing 3-5 high-quality conceptual synonyms or keywords. "
            f"Do NOT generate a long list or repeat terms. Keep the output under 15 words.\n\n"
            f"Query: '{rewritten_query}'\n\n"
            f"Optimized Search Query:"
        )
        try:
            response = llm.invoke(expansion_prompt)
            expanded_query = response.content.strip().strip("'\"")
            print(f"    - Expanded Search Query: {GREEN}{BOLD}\"{expanded_query}\"{RESET}")
            rewritten_query = expanded_query
        except Exception as e:
            print(f"    - Query expansion failed: {e}. Keeping current standalone query.")
        finally:
            analytics.end_stage("rewriting")
            
        # 2. Upgrade retrieval strategy parameters: Force Hybrid, k=10, Rerank=True
        print(f"    - Upgrading retrieval parameters to Hybrid Search with k=10 & Reranking...")
        analytics.record_metric("strategy_name", "Low-Confidence Fallback (Hybrid + k=10)")
        analytics.record_metric("reranking_enabled", True)
        
        # 3. Re-run hybrid retrieval (Global Fallback)
        print(f"    - Clearing domain filter for global fallback search.")
        search_filter = None
        
        analytics.start_stage("retrieval")
        try:
            candidate_docs = retriever.hybrid_retrieve(rewritten_query, k=10, filter=search_filter)
            analytics.end_stage("retrieval")
            
            # 4. Re-run reranking & compression
            analytics.start_stage("reranking")
            final_docs = retriever.rerank_and_compress(rewritten_query, candidate_docs, target_k=3)
            analytics.end_stage("reranking")
            
            # 5. Re-evaluate confidence
            confidence = retriever.calculate_confidence(final_docs, strategy="hybrid")
            analytics.record_metric("confidence_score", confidence)
            analytics.record_metric("chunks_retrieved", len(candidate_docs))
            analytics.record_metric("chunks_sent_to_llm", len(final_docs))
            
            print(f"    - Post-Retry Confidence: {GREEN if confidence >= LOW_CONFIDENCE_THRESHOLD else RED}{confidence*100:.1f}%{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Retry retrieval failed: {e}. Proceeding with original results.{RESET}")
            analytics.end_stage("retrieval")
            analytics.end_stage("reranking")

    # =========================================================================
    # ADAPTIVE RAG STEP 5: ADAPTIVE PROMPT SELECTION & RESPONSE GENERATION
    # =========================================================================
    analytics.start_stage("generation")
    
    # --- Hallucination Prevention ---
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        print(f"\n{GREEN}{BOLD}ANSWER:{RESET}")
        print(f"{BOLD}I could not find relevant information in the documents. The retrieval confidence is too low to provide a factual answer.{RESET}")
        analytics.end_stage("generation")
        analytics.end_stage("total")
        continue
        
    # Construct context string with Chunk IDs and Document sources clearly labeled
    context_blocks = []
    for doc in final_docs:
        source_name = doc.metadata.get("source_name", "unknown_document")
        chunk_id = doc.metadata.get("chunk_id", "unknown_chunk")
        block = f"[Document Source: {source_name} | Chunk ID: {chunk_id}]\n{doc.page_content}"
        context_blocks.append(block)
        
    context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant document chunks found."
    
    # Map query type to target adaptive prompt template
    if q_type == "factual":
        prompt_template = FACTUAL_QA_PROMPT
        formatted_prompt = prompt_template.format(context=context_text, question=query)
    elif q_type == "explanation":
        prompt_template = EXPLANATION_QA_PROMPT
        formatted_prompt = prompt_template.format(context=context_text, question=query)
    elif q_type == "comparison":
        prompt_template = COMPARISON_QA_PROMPT
        formatted_prompt = prompt_template.format(context=context_text, question=query)
    else: # conversational_follow_up
        prompt_template = CONVERSATIONAL_QA_PROMPT
        formatted_prompt = prompt_template.format(
            context=context_text,
            chat_history=history_str if history_str else "No prior history.",
            question=query
        )

    # --- Structured Multi-Question formatting ---
    if is_multi_query:
        formatted_prompt += "\n\nCRITICAL INSTRUCTION: The user has asked multiple distinct questions. You MUST output your answer in clearly separated sections for each concept. For example:\nSection 1: [Concept 1] <answer>\n\nSection 2: [Concept 2] <answer>\nDo not mix the concepts together."
        
    # --- Freshness Detection formatting ---
    is_freshness = router.is_freshness_query(rewritten_query) if hasattr(router, "is_freshness_query") else False
    if is_freshness:
        formatted_prompt += "\n\nCRITICAL INSTRUCTION: The user is asking for current, latest, or real-time information. Explain the core concept using the provided context, but explicitly state that this system does not contain real-time data and the user should verify current values from official sources (like the RBI website)."
        
    print(f"\n{BLUE}[4] Generating response using Adaptive QA Prompt ('{q_type}')...{RESET}")
    try:
        response = llm.invoke(formatted_prompt)
        answer = response.content.strip()
        
        # Save interaction to conversation memory
        chat_memory.save_interaction(query, answer)
        
        analytics.end_stage("generation")
        analytics.end_stage("total")
        
        # Display the final response
        print(f"\n{GREEN}{BOLD}ANSWER:{RESET}")
        print(f"{BOLD}{answer}{RESET}")
        
        # Display Source Citations dynamically if the model actually found info
        strict_refusal = "I could not find relevant information in the documents."
        if answer.strip().lower().rstrip(".") != strict_refusal.lower().rstrip(".") and final_docs:
            print(f"\n{CYAN}{BOLD}📚 SOURCES CITED:{RESET}")
            cited_sources = {}
            for doc in final_docs:
                src = doc.metadata.get("source_name")
                cid = doc.metadata.get("chunk_id")
                # Retrieve the available score metric
                score = doc.metadata.get("rerank_score")
                score_type = "Rerank Score"
                if score is None:
                    score = doc.metadata.get("similarity_score", 0.0)
                    score_type = "Vector L2"
                
                # Retrieve category
                cat = doc.metadata.get("category", "unknown")
                if src not in cited_sources:
                    cited_sources[src] = []
                cited_sources[src].append((cid, score, score_type, cat))
                
            for src, chunks in cited_sources.items():
                print(f"  • {BOLD}{src}{RESET}:")
                for cid, score, stype, cat in chunks:
                    if stype == "Rerank Score":
                        score_color = GREEN if score >= 0 else (YELLOW if score >= -3.0 else RED)
                        print(f"    - [Category: {cat.upper()}] Chunk ID: {CYAN}{cid}{RESET} (Rerank Relevance: {score_color}{score:+.2f}{RESET})")
                    else:
                        score_color = GREEN if score < 0.8 else (YELLOW if score < 1.2 else RED)
                        print(f"    - [Category: {cat.upper()}] Chunk ID: {CYAN}{cid}{RESET} (Vector L2 Distance: {score_color}{score:.2f}{RESET})")
                        
    except Exception as e:
        print(f"{RED}[ERROR] Failed to generate answer from LLM: {e}{RESET}")
        analytics.end_stage("generation")
        analytics.end_stage("total")
        
    print(f"\n{CYAN}========================================================================{RESET}")

    # =========================================================================
    # ADAPTIVE RAG STEP 6: RENDER PERFORMANCE ANALYTICS
    # =========================================================================
    analytics.display_dashboard()
