import os
import sys
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent

def load_and_split_documents(data_dir=str(BASE_DIR / "data"), chunk_size=500, chunk_overlap=50):
    """
    Scans the data directory, loads all .txt files, splits them into manageable 
    overlapping chunks, and assigns unique chunk IDs and source file metadata to each chunk.
    
    This modular design ensures our loader is robust, reusable, and easy to test!
    
    Parameters:
        data_dir (str): Directory containing source text files.
        chunk_size (int): Max character length of each chunk.
        chunk_overlap (int): Characters overlapping between adjacent chunks.
        
    Returns:
        list[Document]: A list of chunked LangChain Document objects with enhanced metadata.
    """
    # 1. Graceful error handling for missing directory
    if not os.path.exists(data_dir):
        print(f"\033[91m[ERROR] Data directory './{data_dir}' does not exist!\033[0m")
        print(f"\033[93mPlease create the '{data_dir}/' folder and add your files.\033[0m")
        return []
        
    # 2. Scanning folder for text and PDF files recursively
    supported_extensions = (".txt", ".pdf")
    file_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.lower().endswith(supported_extensions):
                file_paths.append(os.path.join(root, file))
                
    if not file_paths:
        print(f"\033[91m[ERROR] No supported files (.txt, .pdf) found in the './{data_dir}' folder or subdirectories!\033[0m")
        print(f"\033[93mPlease add text (.txt) or PDF (.pdf) files into './{data_dir}'.\033[0m")
        return []
        
    print(f"\033[94m[loader] Scanning './{data_dir}'... Found {len(file_paths)} files\033[0m")
    
    # 3. Loading the documents
    loaded_documents = []
    for file_path in file_paths:
        try:
            docs = []
            if file_path.lower().endswith(".txt"):
                # Explicitly load text documents with UTF-8 encoding to prevent Windows encoding errors
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
            elif file_path.lower().endswith(".pdf"):
                print(f"\033[94m[loader] Loading PDF file: {file_path}...\033[0m")
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                
            # Add category metadata based on parent folder name
            category = os.path.basename(os.path.dirname(file_path))
            for doc in docs:
                doc.metadata["category"] = category
                
            loaded_documents.extend(docs)
        except Exception as e:
            print(f"\033[91m[WARNING] Could not load file '{file_path}': {e}. Skipping.\033[0m")
            
    if not loaded_documents:
        print("\033[91m[ERROR] No document content could be loaded from files.\033[0m")
        return []

    # 4. Text Splitting (Recursive character splitter keeps paragraphs/sentences intact where possible)
    print(f"\033[94m[loader] Splitting text (chunk_size: {chunk_size}, overlap: {chunk_overlap})...\033[0m")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(loaded_documents)
    
    # 5. Advanced RAG Metadata Enrichment (Injecting Source Name and Unique Chunk IDs)
    # This helps in showing exact citations (e.g., "java_notes.txt - Chunk 4") in the final output!
    chunk_counters = {}
    for chunk in chunks:
        # Extract filename (e.g. "java_notes.txt")
        source_path = chunk.metadata.get("source", "unknown_source")
        filename = os.path.basename(source_path)
        chunk.metadata["source_name"] = filename
        
        # Initialize count or increment for this specific file
        base_name, _ = os.path.splitext(filename)
        chunk_counters[base_name] = chunk_counters.get(base_name, 0) + 1
        
        # Format a clean, unique ID: e.g., "java_notes_chunk_1"
        chunk_id = f"{base_name}_chunk_{chunk_counters[base_name]}"
        chunk.metadata["chunk_id"] = chunk_id
        
    print(f"\033[92m[OK] Successfully loaded and created {len(chunks)} metadata-enriched chunks!\033[0m")
    print(f"\033[94mCreated {len(chunks)} chunks\033[0m")
    return chunks
