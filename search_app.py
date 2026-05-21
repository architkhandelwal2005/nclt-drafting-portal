import os
import warnings
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Suppress developer warnings
warnings.filterwarnings("ignore")

DB_DIR = "faiss_index"

# 1. Configure the Streamlit Page
st.set_page_config(page_title="NCLT Precedent Search", page_icon="⚖️", layout="wide")
st.title("⚖️ NCLT Semantic Precedent Search")
st.write("Search historical judgments using concepts and legal principles.")

# 2. Load the Database (Cached)
@st.cache_resource(show_spinner=False)
def load_database():
    if not os.path.exists(DB_DIR):
        return None
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    v_store = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return v_store

with st.spinner("Loading AI vector database..."):
    vectorstore = load_database()

if vectorstore is None:
    st.error("Database not found! Please run `build_database.py` first to index your PDFs.")
    st.stop()

st.success("Database loaded and ready.")
st.markdown("---")

# 3. The Search Interface
query = st.text_input("Enter your legal research query:", placeholder="e.g., Under what circumstances can the corporate veil be pierced?")

# 4. Optimized Search Execution Logic
if st.button("Search Database") or query:
    if query.strip():
        with st.spinner("Analyzing conceptual vectors..."):
            
            # Execute search with L2 distance scoring
            raw_results = vectorstore.similarity_search_with_score(query, k=5)
            
            # Strict threshold to halt retrieval hallucinations
            DISTANCE_THRESHOLD = 1.5 
            
            # Filter results strictly by threshold
            valid_results = [(doc, score) for doc, score in raw_results if score <= DISTANCE_THRESHOLD]
            
            if not valid_results:
                st.warning(f"No mathematically relevant matches found within the strict distance threshold (< {DISTANCE_THRESHOLD}).")
            else:
                st.subheader(f"📑 Top {len(valid_results)} Relevant Extracts")
                
                # Display results with required citation metadata
                for i, (doc, score) in enumerate(valid_results):
                    source = doc.metadata.get('source', 'Unknown Document')
                    page = doc.metadata.get('page', 'N/A')
                    
                    with st.expander(f"Match {i+1} | Score: {score:.3f} | Source: {source} (Page {page})", expanded=True):
                        st.write(doc.page_content.strip())

        st.markdown("---")
        with st.expander("Advanced Optimization Options", expanded=False):
            st.write("For broader research, utilize Maximal Marginal Relevance (MMR) to force diversity in results.")
            if st.button("Run MMR Search"):
                mmr_results = vectorstore.max_marginal_relevance_search(query, k=3, fetch_k=10)
                for i, doc in enumerate(mmr_results):
                     st.write(f"**Diverse Match {i+1}**: {doc.page_content.strip()}")