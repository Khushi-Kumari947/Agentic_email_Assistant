import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Google Gemini Configuration
# =========================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# =========================
# Embeddings Configuration
# =========================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =========================
# Pinecone Configuration
# =========================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# =========================
# Documents Directory
# =========================

# Railway persistent volume support
if os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
    DATA_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
    DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
else:
    # Local development
    DOCUMENTS_DIR = "documents"

# Create documents directory if not exists
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# =========================
# Chunking Configuration
# =========================
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# =========================
# Agent Configuration
# =========================
AGENT_TEMPERATURE = 0.3
MAX_ITERATIONS = 5