import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Define directory paths
PRECEDENTS_DIR = "Precedents"
DB_DIR = "faiss_index"

# 1. Verification
if not os.path.exists(PRECEDENTS_DIR):
    print(f"Error: Directory '{PRECEDENTS_DIR}' not found. Create it and add PDF files.")
    exit()

documents = []
metadatas = []

print("Step 1: Extracting text from PDFs (Page-Level Segmentation)...")
files_in_dir = [f for f in os.listdir(PRECEDENTS_DIR) if f.lower().endswith(".pdf")]
print(f" -> Found {len(files_in_dir)} PDF(s) in the '{PRECEDENTS_DIR}' folder.")

if not files_in_dir:
    print("No valid PDF files found. Exiting.")
    exit()

for filename in files_in_dir:
    filepath = os.path.join(PRECEDENTS_DIR, filename)
    try:
        doc = fitz.open(filepath)
        page_count = 0
        
        # Iterate and extract strictly by page to preserve citation metadata
        for page_num, page in enumerate(doc):
            text = page.get_text().strip()
            
            # Discard empty pages to prevent polluting the vector space
            if text:
                documents.append(text)
                # Note: page_num is 0-indexed; adding 1 for standard legal citation reading
                metadatas.append({"source": filename, "page": page_num + 1})
                page_count += 1
                
        doc.close()
        print(f" - Read successful: {filename} ({page_count} pages extracted)")
    except Exception as e:
        print(f" - Read failed for {filename}: {e}")

if not documents:
    print("No valid text extracted from PDFs. Exiting.")
    exit()

# 2. Text Chunking
print("\nStep 2: Chunking text into processable segments...")
# Chunk sizes maintained; chunking now inherits the page-level metadata automatically
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.create_documents(documents, metadatas=metadatas)
print(f" -> Generated {len(docs)} highly specific text chunks.")

# 3. Embedding Initialization
print("\nStep 3: Initializing local AI embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Vectorization and FAISS Indexing
print("\nStep 4: Computing mathematical vectors and building FAISS index...")
vectorstore = FAISS.from_documents(docs, embeddings)

# 5. Disk Serialization
print("\nStep 5: Saving isolated FAISS database to disk...")
vectorstore.save_local(DB_DIR)
print(f"Process complete. Production-ready index saved in '{DB_DIR}'.")