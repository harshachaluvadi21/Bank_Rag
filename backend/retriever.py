import os
import sys
import chromadb
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

class AdvancedRetriever:
    """
    Implements a state-of-the-art Advanced Retrieval system:
    1. Secure connection to Chroma DB Cloud for Vector Similarity Search.
    2. Dynamic local BM25 Keyword Search built on top of the vector database chunks.
    3. Hybrid Search merging (Vector + Keyword) with source attribution.
    4. Local Cross-Encoder Reranking using Ms-Marco model.
    5. Context Compression (duplicate removal & relevance score filtering).
    """
    
    def __init__(self, embeddings_model, collection_name="rag_collection"):
        self.embeddings = embeddings_model
        self.collection_name = collection_name
        self.db = None
        self.bm25_retriever = None
        self.cross_encoder = None
        
        # Connect to Chroma Cloud on initialization
        self._connect_chroma_cloud()
        
    def _connect_chroma_cloud(self):
        """Establishes connection to Chroma DB Cloud using credentials in .env."""
        chroma_host = os.getenv("CHROMA_HOST")
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT")
        chroma_database = os.getenv("CHROMA_DATABASE")
        
        if not all([chroma_host, chroma_api_key, chroma_tenant, chroma_database]):
            print("\033[91m[ERROR] Chroma DB Cloud configuration is incomplete in .env!\033[0m")
            sys.exit(1)
            
        print("\033[94m[retriever] Establishing secure connection to Chroma DB Cloud...\033[0m")
        try:
            self.client = chromadb.CloudClient(
                cloud_host=chroma_host,
                api_key=chroma_api_key,
                tenant=chroma_tenant,
                database=chroma_database
            )
            
            # Check if collection exists
            collections = [c.name for c in self.client.list_collections()]
            self.collection_exists = self.collection_name in collections
            
            if self.collection_exists:
                print(f"\033[94m[retriever] Found existing collection '{self.collection_name}'. Loading index...\033[0m")
                self.db = Chroma(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings
                )
                # Load BM25 index on start since the vector DB already has documents
                self.sync_bm25()
            else:
                print(f"\033[93m[retriever] Collection '{self.collection_name}' not found on the cloud.\033[0m")
        except Exception as e:
            print(f"\033[91m[ERROR] Failed to connect to Chroma DB Cloud: {e}\033[0m")
            sys.exit(1)

    def _clean_document_metadata(self, doc: Document):
        """Ensures retrieved documents have source_name and chunk_id populated."""
        import hashlib
        
        # 1. Fallback for source_name
        if "source" in doc.metadata and ("source_name" not in doc.metadata or not doc.metadata["source_name"]):
            doc.metadata["source_name"] = os.path.basename(doc.metadata["source"])
        
        if "source_name" not in doc.metadata or not doc.metadata["source_name"]:
            doc.metadata["source_name"] = "Unknown Source"
            
        # 2. Fallback for chunk_id
        if "chunk_id" not in doc.metadata or not doc.metadata["chunk_id"]:
            # Generate a stable, clean ID based on document name or hash of page content
            content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()[:8]
            base_name = os.path.splitext(doc.metadata["source_name"])[0]
            doc.metadata["chunk_id"] = f"{base_name}_chunk_{content_hash}"

    def sync_bm25(self):
        """
        Dynamically downloads all document chunks from Chroma DB Cloud and builds the local
        BM25 keyword search index. This is an advanced, production-grade technique!
        """
        if not self.db:
            return
            
        try:
            print("\033[94m[retriever] Syncing local BM25 index with Chroma Cloud database...\033[0m")
            db_data = self.db.get()
            
            if not db_data or not db_data['documents']:
                print("\033[93m[retriever] Chroma Cloud collection is empty. BM25 not initialized.\033[0m")
                return
                
            docs = []
            for text, metadata, doc_id in zip(db_data['documents'], db_data['metadatas'], db_data['ids']):
                # Reconstruct LangChain document objects with full metadata
                doc = Document(page_content=text, metadata={**metadata})
                self._clean_document_metadata(doc)
                # Overwrite chunk_id with Chroma doc_id if it's a valid custom ID
                if doc_id and len(doc_id) > 10 and "-" not in doc_id:
                    doc.metadata["chunk_id"] = doc_id
                docs.append(doc)
                
            # Initialize BM25 retriever locally
            self.bm25_retriever = BM25Retriever.from_documents(docs)
            # Fetch up to 10 chunks per query by default
            self.bm25_retriever.k = 10
            print(f"\033[92m[OK] BM25 Index initialized locally with {len(docs)} chunks!\033[0m")
        except Exception as e:
            print(f"\033[91m[WARNING] Could not sync local BM25 index: {e}\033[0m")

    def reset_collection(self):
        """Deletes the current collection from Chroma DB Cloud so it can be re-indexed."""
        try:
            print(f"\033[93m[retriever] Wiping existing collection '{self.collection_name}' from Chroma Cloud...\033[0m")
            self.client.delete_collection(self.collection_name)
            self.collection_exists = False
            self.db = None
            self.bm25_retriever = None
            print("\033[92m[OK] Chroma Cloud collection wiped successfully!\033[0m")
        except Exception as e:
            # If the collection didn't exist or deletion failed, catch it gracefully
            self.collection_exists = False
            self.db = None
            self.bm25_retriever = None

    def initialize_with_documents(self, chunks):
        """
        Saves document chunks to Chroma DB Cloud in batches of 200 to stay within 
        the strict free-tier Upsert limits (max 300 per request), then synchronizes BM25 index.
        """
        print(f"\033[94m[retriever] Generating embeddings and saving to Chroma Cloud in batches of 200...\033[0m")
        try:
            chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
            
            # Batch size set to 200 (very safe and well below the 300 limit)
            batch_size = 200
            
            # Initialize with the first batch
            first_batch_docs = chunks[:batch_size]
            first_batch_ids = chunk_ids[:batch_size]
            
            print(f"    - Uploading batch 1 ({len(first_batch_docs)} chunks)...")
            self.db = Chroma.from_documents(
                documents=first_batch_docs,
                embedding=self.embeddings,
                client=self.client,
                collection_name=self.collection_name,
                ids=first_batch_ids
            )
            
            # Upload subsequent batches using add_documents
            for i in range(batch_size, len(chunks), batch_size):
                batch_docs = chunks[i : i + batch_size]
                batch_ids = chunk_ids[i : i + batch_size]
                batch_num = (i // batch_size) + 1
                print(f"    - Uploading batch {batch_num} ({len(batch_docs)} chunks)...")
                self.db.add_documents(documents=batch_docs, ids=batch_ids)
                
            print("\033[92m[OK] Vector database successfully created on Chroma Cloud!\033[0m")
            self.collection_exists = True
            
            # Sync the local BM25 retriever
            self.sync_bm25()
        except Exception as e:
            print(f"\033[91m[ERROR] Failed to save embeddings to Chroma Cloud: {e}\033[0m")
            sys.exit(1)

    def hybrid_retrieve(self, query: str, k=10, filter=None) -> list[Document]:
        """
        Retrieves top k candidate chunks from both vector similarity and BM25 search.
        
        Parameters:
            query (str): The search query (ideally rewritten standalone).
            k (int): Number of chunks to fetch from each retriever.
            filter (dict): Optional metadata filter for Chroma DB.
            
        Returns:
            list[Document]: Merged candidate chunks with source retriever tags.
        """
        if not self.db:
            print("\033[91m[ERROR] Database not initialized. Call initialize_with_documents first.\033[0m")
            return []
            
        # 1. Retrieve from Vector Search
        # Chroma similarity search returns top matches
        vector_docs = self.db.similarity_search(query, k=k, filter=filter)
        
        # 2. Retrieve from BM25 (Keyword Search)
        bm25_docs = []
        if self.bm25_retriever:
            try:
                # If filter is applied, fetch more chunks from BM25 to ensure we have enough post-filtering
                fetch_k = k * 5 if filter else k
                self.bm25_retriever.k = fetch_k
                all_bm25_docs = self.bm25_retriever.invoke(query)
                
                # Apply manual filtering to BM25 results
                if filter and "$or" in filter:
                    allowed_cats = [cond["category"] for cond in filter["$or"] if "category" in cond]
                    bm25_docs = [d for d in all_bm25_docs if d.metadata.get("category") in allowed_cats][:k]
                elif filter and "category" in filter:
                    bm25_docs = [d for d in all_bm25_docs if d.metadata.get("category") == filter["category"]][:k]
                else:
                    bm25_docs = all_bm25_docs[:k]
            except Exception as e:
                print(f"\033[91m[WARNING] BM25 keyword search failed: {e}\033[0m")
        else:
            print("\033[93m[WARNING] BM25 retriever is not active. Using Vector search only.\033[0m")
            
        # 3. Hybrid Merging and Deduplication
        # Merge and track which retriever found which chunk
        seen_chunks = {} # Maps chunk ID or text to Document
        
        for doc in vector_docs:
            self._clean_document_metadata(doc)
            cid = doc.metadata.get("chunk_id") or doc.page_content
            # Inject retriever origin
            doc.metadata["retrieved_by"] = "Vector Search"
            seen_chunks[cid] = doc
            
        for doc in bm25_docs:
            self._clean_document_metadata(doc)
            cid = doc.metadata.get("chunk_id") or doc.page_content
            if cid in seen_chunks:
                # Document was found by BOTH
                seen_chunks[cid].metadata["retrieved_by"] = "Hybrid (Vector + BM25)"
            else:
                doc.metadata["retrieved_by"] = "BM25 Keyword"
                seen_chunks[cid] = doc
                
        merged_candidates = list(seen_chunks.values())
        print(f"\033[94m[retriever] Hybrid retrieval fetched {len(merged_candidates)} unique candidate chunks (Vector: {len(vector_docs)}, BM25: {len(bm25_docs)}).\033[0m")
        return merged_candidates

    def rerank_and_compress(self, query: str, candidates: list[Document], target_k=3) -> list[Document]:
        """
        Loads a local Cross-Encoder model and scores semantic relevance of chunks
        against the query, then removes irrelevant chunks (Context Compression).
        
        Parameters:
            query (str): The search query.
            candidates (list[Document]): Chunks retrieved by hybrid search.
            target_k (int): Number of chunks to select after reranking.
            
        Returns:
            list[Document]: Sorted and filtered top chunks with confidence scores.
        """
        if not candidates:
            return []
            
        # 1. Lazy load local Cross-Encoder (to keep initial startup lightning fast)
        if self.cross_encoder is None:
            print("\033[94m[retriever] Loading local Cross-Encoder model ('ms-marco-MiniLM-L-6-v2')...\033[0m")
            try:
                from sentence_transformers import CrossEncoder
                self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
                print("\033[92m[OK] Cross-Encoder model loaded successfully!\033[0m")
            except Exception as e:
                print(f"\033[91m[ERROR] Failed to load Cross-Encoder: {e}\033[0m")
                print("\033[93mReranking skipped; falling back to vector ordering.\033[0m")
                return candidates[:target_k]
                
        # 2. Prepare pairs for scoring: [(Query, Text1), (Query, Text2), ...]
        pairs = [[query, doc.page_content] for doc in candidates]
        
        # 3. Compute scores
        # Returns a list of floating-point logits. Higher means more relevant.
        scores = self.cross_encoder.predict(pairs)
        
        # 4. Inject scores and sort
        for doc, score in zip(candidates, scores):
            doc.metadata["rerank_score"] = float(score)
            
        # Sort in descending order of relevance
        candidates.sort(key=lambda d: d.metadata["rerank_score"], reverse=True)
        
        # 5. Context Compression / Relevance Filtering
        # MS-Marco Cross-Encoder scores are raw logits:
        # > 0.0 is extremely relevant, -1.0 to -5.0 is weakly relevant, < -5.0 is irrelevant.
        # We will filter out completely irrelevant chunks (score < -5.0) to avoid LLM confusion!
        RELEVANCE_THRESHOLD = -7.0
        relevant_chunks = [d for d in candidates if d.metadata["rerank_score"] >= RELEVANCE_THRESHOLD]
        
        filtered_out_count = len(candidates) - len(relevant_chunks)
        if filtered_out_count > 0:
            print(f"\033[93m[retriever] Compressed context: Filtered out {filtered_out_count} irrelevant chunks (score < {RELEVANCE_THRESHOLD}).\033[0m")
            
        # Select top target_k
        top_chunks = relevant_chunks[:target_k]
        return top_chunks

    def vector_retrieve(self, query: str, k=3, filter=None) -> list:
        """
        Retrieves top k candidate chunks using vector similarity search only.
        Also obtains the vector similarity L2 distance to inject into metadata.
        
        Parameters:
            query (str): The search query.
            k (int): Number of chunks to fetch.
            filter (dict): Optional metadata filter for Chroma DB.
            
        Returns:
            list[Document]: Retrieved chunks with source attribution and vector scores.
        """
        if not self.db:
            print("\033[91m[ERROR] Database not initialized. Call initialize_with_documents first.\033[0m")
            return []
            
        try:
            # Chroma similarity_search_with_score returns list of (Document, L2_distance)
            docs_with_scores = self.db.similarity_search_with_score(query, k=k, filter=filter)
            
            retrieved_docs = []
            for doc, score in docs_with_scores:
                self._clean_document_metadata(doc)
                doc.metadata["retrieved_by"] = "Vector Search"
                doc.metadata["similarity_score"] = float(score)
                retrieved_docs.append(doc)
                
            print(f"\033[94m[retriever] Vector search retrieved {len(retrieved_docs)} chunks.\033[0m")
            return retrieved_docs
        except Exception as e:
            print(f"\033[91m[WARNING] Vector search with score failed: {e}. Falling back to standard search...\033[0m")
            # Fallback
            standard_docs = self.db.similarity_search(query, k=k, filter=filter)
            for doc in standard_docs:
                self._clean_document_metadata(doc)
                doc.metadata["retrieved_by"] = "Vector Search"
                doc.metadata["similarity_score"] = 0.5 # dummy fallback distance
            return standard_docs

    def calculate_confidence(self, chunks: list, strategy: str) -> float:
        """
        Calculates a confidence score between 0.0 and 1.0 indicating retrieval quality:
        - For vector search: maps the best (lowest) L2 distance score to [0, 1].
          Formula: max(0.0, 1.0 - (min_distance / 1.5))
        - For reranked searches: maps the best (highest) Cross-Encoder logit score to [0, 1]
          Formula: 1.0 / (1.0 + exp(-(max_score + 2.0) / 2.0))
          
        Parameters:
            chunks (list): Chunks returned from the retrieval pipeline.
            strategy (str): 'vector' or 'hybrid' (which indicates reranked).
            
        Returns:
            float: A confidence score between 0.0 and 1.0.
        """
        import math
        
        if not chunks:
            return 0.0
            
        if strategy == "vector":
            # For vector only search, we check similarity_score (L2 distance)
            # Find the minimum distance (best match)
            distances = [doc.metadata.get("similarity_score") for doc in chunks if "similarity_score" in doc.metadata]
            if not distances:
                return 0.5 # Default middle score if metadata missing
                
            min_dist = min(distances)
            # Typical L2 distances range from 0 (perfect match) to 1.5+ (weak match)
            confidence = max(0.0, min(1.0, 1.0 - (min_dist / 1.5)))
            return confidence
        else:
            # For reranked hybrid search, we check rerank_score (Ms-Marco logit score)
            # Find the maximum rerank score (best match)
            scores = [doc.metadata.get("rerank_score") for doc in chunks if "rerank_score" in doc.metadata]
            if not scores:
                return 0.0
                
            max_score = max(scores)
            # Ms-Marco MiniLM-L-6-v2 typical relevant scores are above -2.0.
            # Sigmoid scaling maps logits to 0-1 nicely
            confidence = 1.0 / (1.0 + math.exp(-(max_score + 2.0) / 2.0))
            return confidence

