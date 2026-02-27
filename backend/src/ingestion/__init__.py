# src/ingestion/__init__.py
import sys
print("📚 Ingestion module loading...", file=sys.stderr)

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStore
from src.config import DOCUMENTS_DIR, VECTOR_STORE_PATH

# Create instance WITHOUT loading models
print("📚 Creating VectorStore instance...", file=sys.stderr)
vector_store = VectorStore()  # This is now safe - doesn't load models
print("📚 VectorStore instance created", file=sys.stderr)

def run_ingestion():
    """Main ingestion function - reads from DOCUMENTS_DIR"""
    try:
        print(f"📂 Reading documents from: {DOCUMENTS_DIR}", file=sys.stderr)
        
        loader = DocumentLoader()
        documents = loader.load_documents(DOCUMENTS_DIR)
        
        if not documents:
            return {
                "status": "error",
                "message": "No documents found in the documents directory"
            }
        
        print(f"📄 Found {len(documents)} documents", file=sys.stderr)
        
        # Force encoder to load now (during ingestion, not during import)
        if vector_store.encoder is None:
            print("📦 Loading encoder for ingestion...", file=sys.stderr)
            _ = vector_store.encoder  # Trigger lazy load
        
        chunked_docs = loader.chunk_documents(documents)
        print(f"🔪 Created {len(chunked_docs)} chunks", file=sys.stderr)
        
        vector_store.build_index(chunked_docs)
        vector_store.save()
        
        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": len(chunked_docs),
            "message": f"Successfully processed {len(documents)} documents"
        }
    except Exception as e:
        print(f"❌ Ingestion error: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

# Don't auto-load on startup
print("📚 Ingestion module loaded (models not loaded yet)", file=sys.stderr)