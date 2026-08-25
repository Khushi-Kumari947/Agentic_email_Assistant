# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash-lite"   
# "gemini-2.5-flash"

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "email-assistant")

# Google Drive
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")  # Add this

# Chunking Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Agent Configuration
AGENT_TEMPERATURE = 0.3
MAX_ITERATIONS = 5