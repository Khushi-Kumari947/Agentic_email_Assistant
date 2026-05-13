# src/ingestion/__init__.py
import sys
import os
import tempfile

print("📚 Ingestion module loading...", file=sys.stderr)

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStore
from src.utils.drive_downloader import download_from_gdrive

# Create a temporary or local directory for downloaded documents
DOCUMENTS_DIR = "documents"  # This is the download destination

print("📚 Creating VectorStore instance...", file=sys.stderr)
vector_store = VectorStore()
print("📚 VectorStore instance created", file=sys.stderr)

def run_ingestion():
    """Main ingestion function - downloads from Google Drive and indexes"""
    try:
        # First, download documents from Google Drive
        print("📂 Downloading documents from Google Drive...", file=sys.stderr)
        download_from_gdrive()  # This uses GDRIVE_FOLDER_ID env var and downloads to "documents"
        
        print(f"📂 Loading documents from: {DOCUMENTS_DIR}", file=sys.stderr)
        
        # Force encoder to load now (during ingestion, not during import)
        if vector_store.encoder is None:
            print("📦 Loading encoder for ingestion...", file=sys.stderr)
            _ = vector_store.encoder  # Trigger lazy load
        
        loader = DocumentLoader()
        
        # Check if documents directory exists and has files
        if not os.path.exists(DOCUMENTS_DIR):
            return {
                "status": "error",
                "message": "Failed to download documents from Google Drive"
            }
        
        documents = loader.load_documents(DOCUMENTS_DIR)
        
        if not documents:
            return {
                "status": "error",
                "message": "No documents found after download. Check your Google Drive folder."
            }
        
        print(f"📄 Found {len(documents)} documents", file=sys.stderr)
        
        chunked_docs = loader.chunk_documents(documents)
        print(f"🔪 Created {len(chunked_docs)} chunks", file=sys.stderr)
        
        vector_store.build_index(chunked_docs)
        
        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": len(chunked_docs),
            "message": f"Successfully processed {len(documents)} documents"
        }
    except Exception as e:
        print(f"❌ Ingestion error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {"status": "error", "message": str(e)}

print("📚 Ingestion module loaded", file=sys.stderr)