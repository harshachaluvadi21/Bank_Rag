import os
import sys
import time
from dotenv import load_dotenv

# Load env variables (for Chroma DB credentials, API keys, etc.)
load_dotenv()

from embeddings import get_embeddings_model
from retriever import AdvancedRetriever
from router import QueryRouter, BankingDomainRouter
from llm import initialize_llm

def main():
    print("1. Initializing embeddings model...")
    embeddings = get_embeddings_model()
    
    print("2. Initializing AdvancedRetriever (Connects to existing DB)...")
    retriever = AdvancedRetriever(embeddings_model=embeddings)
    
    print("\n--- RETRIEVAL TESTS WITH ENHANCED ROUTING ---")
    
    llm = initialize_llm()
    router = QueryRouter(llm=llm)
    domain_router = BankingDomainRouter()
    
    queries = [
        "What is CRR? What are KYC requirements? What does SIP stand for?",
        "Explain EMI and Credit Score.",
        "Compare Home Loan and SIP.",
        "Why is an Emergency Fund important?",
        "What is AI?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n=========================================")
        print(f"Query {i}: {query}")
        print(f"=========================================")
        
        start_time = time.time()
        
        # 1. Routing for Complexity (Latency Tracked)
        classification = router.classify_query(query)
        strategy = router.get_strategy(classification["complexity"])
        strategy_name = strategy["strategy_name"]
        routing_latency = (time.time() - start_time) * 1000
        
        print(f"Routing Latency: {routing_latency:.2f} ms")
        print(f"Strategy: {strategy_name}")
        
        # 2. Query Decomposition
        sub_queries = router.decompose_query(query)
        print(f"Decomposed Sub-queries ({len(sub_queries)}): {sub_queries}")
        
        all_candidate_docs = []
        all_final_docs = []
        all_confidences = []
        all_categories = set()
        all_filters = []
        
        for sq in sub_queries:
            # 3. Routing for Domain Category
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
            
            # 4. Retrieve
            if strategy["retriever"] == "vector":
                candidates = retriever.vector_retrieve(sq, k=strategy["k"], filter=search_filter)
            else:
                candidates = retriever.hybrid_retrieve(sq, k=strategy["k"], filter=search_filter)
                
            if strategy["rerank"]:
                final_docs = retriever.rerank_and_compress(sq, candidates, target_k=3)
                confidence = retriever.calculate_confidence(final_docs, strategy="hybrid")
            else:
                final_docs = candidates[:3]
                confidence = retriever.calculate_confidence(final_docs, strategy="vector")
                
            all_candidate_docs.extend(candidates)
            all_final_docs.extend(final_docs)
            all_confidences.append(confidence)
            
        # Deduplicate
        seen_ids = set()
        dedup_final_docs = []
        for doc in all_final_docs:
            cid = doc.metadata.get("chunk_id")
            if cid not in seen_ids:
                seen_ids.add(cid)
                dedup_final_docs.append(doc)
                
        final_docs = dedup_final_docs
        categories = list(all_categories)
        confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        print(f"Categories Detected: {categories if categories else 'None'}")
        print(f"Filter Applied: {all_filters}")
        print(f"Retrieval Confidence: {confidence*100:.1f}%")
        print(f"Total Chunks Retrieved (Deduplicated): {len(final_docs)}")
        
        # Out of Domain check
        if confidence < 0.45 and not categories:
            print("\n[OUT OF DOMAIN REJECTION]: This Banking Adaptive RAG specializes in Banking and Financial Services. The query appears to be outside the supported domain.")
            continue
            
        # Display top chunks
        for j, doc in enumerate(final_docs[:3], 1):
            source_name = doc.metadata.get("source_name", "Unknown")
            category = doc.metadata.get("category", "Unknown")
            retrieved_by = doc.metadata.get("retrieved_by", "Unknown")
            
            print(f"  Chunk {j}:")
            print(f"    - source_name: {source_name}")
            print(f"    - category: {category}")
            print(f"    - retrieved_by: {retrieved_by}")

if __name__ == "__main__":
    main()
