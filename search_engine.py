import os
import warnings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Suppress developer warnings
warnings.filterwarnings("ignore")

DB_DIR = "faiss_index"

# 1. Verification
if not os.path.exists(DB_DIR):
    print("Error: Database not found. Please run build_database.py first.")
    exit()

print("Loading local AI model and connecting to FAISS database... ")

# 2. Load the embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. Load the vectorstore
vectorstore = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)

print("\n" + "="*60)
print("⚖️  NCLT PRECEDENT SEARCH ENGINE INITIALIZED  ⚖️")
print("="*60)

# Define distance threshold (Lower score = higher mathematical similarity)
# NOTE: This value requires empirical tuning based on the specific vector distribution.
DISTANCE_THRESHOLD = 1.5 

# 4. Interactive Search Loop
while True:
    query = input("\nEnter your legal research query (or type 'exit' to quit):\n> ")
    
    if query.lower() == 'exit':
        print("Shutting down search engine. Terminated.")
        break
        
    if not query.strip():
        continue
        
    print(f"\nAnalyzing conceptual vectors for: '{query}'...")
    
    # Execute search with L2 distance scoring
    raw_results = vectorstore.similarity_search_with_score(query, k=5)
    
    # Filter out statistically irrelevant matches
    valid_results = [(doc, score) for doc, score in raw_results if score <= DISTANCE_THRESHOLD]
    
    if not valid_results:
        print(f"WARNING: No matches found within the strict distance threshold (< {DISTANCE_THRESHOLD}).")
        continue
        
    print("\n" + "-"*60)
    print(f"TOP {len(valid_results)} RELEVANT JUDGMENT EXTRACTS")
    print("-" * 60)
    
    # Output formatted results with verifiable metrics and precise citations
    for i, (doc, score) in enumerate(valid_results):
        source = doc.metadata.get('source', 'Unknown Document')
        page = doc.metadata.get('page', 'N/A')
        
        print(f"\nMATCH {i+1} | Score: {score:.3f} | Source: {source} (Page {page})")
        print("~"*60)
        print(doc.page_content.strip()) 
        print("~"*60)