from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStore
from src.config import DOCUMENTS_DIR, VECTOR_STORE_PATH

# Initialize vector store (singleton)
vector_store = VectorStore()

def run_ingestion():
    """Main ingestion function - reads from DOCUMENTS_DIR"""
    try:
        print(f"📂 Reading documents from: {DOCUMENTS_DIR}")
        
        # Load documents from DOCUMENTS_DIR
        loader = DocumentLoader()  # ✅ Now defined!
        documents = loader.load_documents(DOCUMENTS_DIR)
        
        if not documents:
            return {
                "status": "error",
                "message": "No documents found in the documents directory"
            }
        
        print(f"📄 Found {len(documents)} documents")
        
        # Chunk and index
        chunked_docs = loader.chunk_documents(documents)
        print(f"🔪 Created {len(chunked_docs)} chunks")
        
        # Build and save vector store
        vector_store.build_index(chunked_docs)
        vector_store.save()
        
        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": len(chunked_docs),
            "message": f"Successfully processed {len(documents)} documents"
        }
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        return {"status": "error", "message": str(e)}

# Try to load existing vector store on startup
try:
    if vector_store.load():
        print(f"✅ Loaded existing vector store from {VECTOR_STORE_PATH}")
    else:
        print(f"⚠️ No existing vector store found at {VECTOR_STORE_PATH}")
except Exception as e:
    print(f"⚠️ Could not load vector store: {e}")