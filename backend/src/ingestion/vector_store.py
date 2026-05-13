# src/ingestion/vector_store.py

import sys
from sentence_transformers import SentenceTransformer
import numpy as np
from pinecone import Pinecone

from src.config import (
    EMBEDDING_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME
)


class VectorStore:
    def __init__(self):
        print(
            "📦 Initializing Pinecone VectorStore...",
            file=sys.stderr
        )

        self._encoder = None
        self.embedding_dim = None

        # Pinecone namespace
        self.namespace = "default"

        # Initialize Pinecone
        self.pc = Pinecone(
            api_key=PINECONE_API_KEY
        )

        self.index = self.pc.Index(
            PINECONE_INDEX_NAME
        )

        print(
            "✅ Pinecone initialized",
            file=sys.stderr
        )

    @property
    def encoder(self):
        if self._encoder is None:

            print(
                "📦 Loading Sentence Transformer model...",
                file=sys.stderr
            )

            self._encoder = SentenceTransformer(
                EMBEDDING_MODEL
            )

            self.embedding_dim = (
                self._encoder.get_sentence_embedding_dimension()
            )

            print(
                f"✅ Model loaded. Embedding dimension: {self.embedding_dim}",
                file=sys.stderr
            )

        return self._encoder

    def create_embeddings(self, texts):
        return self.encoder.encode(
            texts,
            convert_to_numpy=True
        )

    def build_index(self, chunked_docs):
        """
        Generate embeddings and upload to Pinecone with metadata.
        """
        print("🗑 Clearing old Pinecone vectors...", file=sys.stderr)

        # Safely delete old vectors
        try:
            self.index.delete(
                delete_all=True,
                namespace=self.namespace
            )

            print("✅ Old vectors deleted", file=sys.stderr)

        except Exception as e:
            print(
                f"⚠️ No existing namespace yet: {e}",
                file=sys.stderr
            )

        print(
            f"🔨 Uploading {len(chunked_docs)} chunks to Pinecone...",
            file=sys.stderr
        )

        texts = [
            doc["text"]
            for doc in chunked_docs
        ]

        embeddings = self.create_embeddings(texts)

        vectors = []

        for i, (embedding, doc) in enumerate(
            zip(embeddings, chunked_docs)
        ):
            # Build metadata with source information if available
            metadata = {
                "text": doc["text"],
                "chunk_id": i
            }

            # Add source if available in document metadata
            if "metadata" in doc and doc["metadata"]:
                if "source" in doc["metadata"]:
                    metadata["source"] = doc["metadata"]["source"]
                if "document_name" in doc["metadata"]:
                    metadata["document_name"] = doc["metadata"]["document_name"]

            vectors.append({
                "id": str(i),
                "values": embedding.tolist(),
                "metadata": metadata
            })

        # Upload vectors to Pinecone
        self.index.upsert(
            vectors=vectors,
            namespace=self.namespace
        )

        print(
            f"✅ Uploaded {len(vectors)} vectors to Pinecone",
            file=sys.stderr
        )

    def similarity_search(self, query, k=3):
        """
        Query Pinecone for similar documents.
        """
        print(
            f"🔍 Performing similarity search for: {query}",
            file=sys.stderr
        )

        query_embedding = self.create_embeddings(
            [query]
        )

        results = self.index.query(
            vector=query_embedding.tolist()[0],
            top_k=k,
            include_metadata=True,
            namespace=self.namespace
        )

        formatted_results = []

        matches = results.get("matches", [])

        for match in matches:
            metadata = match.get("metadata", {})

            # Build document with metadata for compatibility
            formatted_results.append({
                "document": {
                    "text": metadata.get("text", ""),
                    "metadata": {
                        "source": metadata.get("source", "Policy Document"),
                        "chunk_id": metadata.get("chunk_id", 0),
                        "document_name": metadata.get("document_name", "Unknown")
                    }
                },
                "similarity_score": float(
                    match.get("score", 0)
                )
            })

        print(
            f"✅ Retrieved {len(formatted_results)} matching documents",
            file=sys.stderr
        )

        return formatted_results