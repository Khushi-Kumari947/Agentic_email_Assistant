# src/ingestion/__init__.py

import sys

print("📚 Ingestion module loading...", file=sys.stderr)

from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStore
from src.ingestion.gdrive_loader import download_from_gdrive
from src.config import DOCUMENTS_DIR

print("📚 Creating VectorStore instance...", file=sys.stderr)

vector_store = VectorStore()

print("📚 VectorStore instance created", file=sys.stderr)


def run_ingestion():
    """
    Main ingestion function:
    Downloads documents from Google Drive
    and uploads embeddings to Pinecone.
    """

    try:
        download_from_gdrive()

        print(
            f"📂 Reading documents from: {DOCUMENTS_DIR}",
            file=sys.stderr
        )

        loader = DocumentLoader()

        documents = loader.load_documents(DOCUMENTS_DIR)

        if not documents:
            return {
                "status": "error",
                "message": "No documents found in the documents directory"
            }

        print(
            f"📄 Found {len(documents)} documents",
            file=sys.stderr
        )

        # Load embedding model
        _ = vector_store.encoder

        # Chunk documents
        chunked_docs = loader.chunk_documents(documents)

        print(
            f"🔪 Created {len(chunked_docs)} chunks",
            file=sys.stderr
        )

        # Upload to Pinecone
        vector_store.build_index(chunked_docs)

        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": len(chunked_docs),
            "message": f"Successfully processed {len(documents)} documents"
        }

    except Exception as e:
        print(f"❌ Ingestion error: {e}", file=sys.stderr)

        return {
            "status": "error",
            "message": str(e)
        }


print(
    "📚 Ingestion module loaded (models not loaded yet)",
    file=sys.stderr
)