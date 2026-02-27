# src/ingestion/vector_store.py
import sys
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from src.config import EMBEDDING_MODEL, VECTOR_STORE_PATH

class VectorStore:
    def __init__(self):
        """Initialize without loading models"""
        print("📦 VectorStore.__init__ - creating empty instance", file=sys.stderr)
        self._encoder = None
        self.index = None
        self.documents = []
        self.embedding_dim = None  # Will be set when encoder loads
        self.store_path = VECTOR_STORE_PATH
    
    @property
    def encoder(self):
        """Lazy load the encoder only when needed"""
        if self._encoder is None:
            print("📦 Loading Sentence Transformer model...", file=sys.stderr)
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
            self.embedding_dim = self._encoder.get_sentence_embedding_dimension()
            print(f"📦 Model loaded. Embedding dimension: {self.embedding_dim}", file=sys.stderr)
        return self._encoder
    
    def create_embeddings(self, texts):
        """Create embeddings using the lazy-loaded encoder"""
        return self.encoder.encode(texts, convert_to_numpy=True)
    
    def similarity_search(self, query, k=3):
        """Search for similar documents"""
        if self.index is None:
            print("📦 Index not loaded, attempting to load...", file=sys.stderr)
            if not self.load():
                return []
        
        # Create query embedding
        query_embedding = self.create_embeddings([query])
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        # Return documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "similarity_score": float(1 / (1 + distances[0][i]))
                })
        
        return results
    
    def save(self):
        """Save index and documents"""
        if self.index is None:
            raise ValueError("No index to save")
        
        faiss.write_index(self.index, f"{self.store_path}.faiss")
        with open(f"{self.store_path}.pkl", "wb") as f:
            pickle.dump(self.documents, f)
        print(f"✅ Vector store saved to {self.store_path}", file=sys.stderr)
    
    def load(self):
        """Load index and documents"""
        try:
            self.index = faiss.read_index(f"{self.store_path}.faiss")
            with open(f"{self.store_path}.pkl", "rb") as f:
                self.documents = pickle.load(f)
            print(f"✅ Vector store loaded from {self.store_path}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"⚠️ Could not load vector store: {e}", file=sys.stderr)
            return False