import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"  # or "gemini-1.5-flash" for faster/cheaper

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Use Railway persistent volume in production
if os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
    DATA_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
    DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
    VECTOR_STORE_PATH = os.path.join(DATA_DIR, "faiss_index")
else:
    # Local development
    DOCUMENTS_DIR = "documents"
    VECTOR_STORE_PATH = "faiss_index"

# Create directories if they don't exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
# For vector store path, need to handle filename separately
vector_store_dir = os.path.dirname(VECTOR_STORE_PATH)
if vector_store_dir:  # Only create if there's a directory path
    os.makedirs(vector_store_dir, exist_ok=True)

# Chunking Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Agent Configuration
AGENT_TEMPERATURE = 0.3
MAX_ITERATIONS = 5