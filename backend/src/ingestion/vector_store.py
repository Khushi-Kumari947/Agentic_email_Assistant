# src/ingestion/vector_store.py
import sys
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np
from src.config import EMBEDDING_MODEL, VECTOR_STORE_PATH

class VectorStore:
    def __init__(self):
        print("📦 VectorStore.__init__ - creating empty instance", file=sys.stderr)
        self._encoder = None
        self.index = None
        self.documents = []
        self.embedding_dim = None
        self.store_path = VECTOR_STORE_PATH
    
    @property
    def encoder(self):
        if self._encoder is None:
            print("📦 Loading Sentence Transformer model...", file=sys.stderr)
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
            self.embedding_dim = self._encoder.get_sentence_embedding_dimension()
            print(f"📦 Model loaded. Embedding dimension: {self.embedding_dim}", file=sys.stderr)
        return self._encoder
    
    def create_embeddings(self, texts):
        return self.encoder.encode(texts, convert_to_numpy=True)
    
    def build_index(self, chunked_docs):
        """Build FAISS index from chunked documents"""
        print(f"🔨 Building index from {len(chunked_docs)} chunks...", file=sys.stderr)
        
        texts = [doc["text"] for doc in chunked_docs]
        embeddings = self.create_embeddings(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype(np.float32))
        
        self.documents = chunked_docs
        
        print(f"✅ Index built with {self.index.ntotal} vectors", file=sys.stderr)
    
    def similarity_search(self, query, k=3):
        if self.index is None:
            print("📦 Index not loaded, attempting to load...", file=sys.stderr)
            if not self.load():
                return []
        
        query_embedding = self.create_embeddings([query])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "similarity_score": float(1 / (1 + distances[0][i]))
                })
        
        return results
    
    def save(self):
        if self.index is None:
            raise ValueError("No index to save")
        
        faiss.write_index(self.index, f"{self.store_path}.faiss")
        with open(f"{self.store_path}.pkl", "wb") as f:
            pickle.dump(self.documents, f)
        print(f"✅ Vector store saved to {self.store_path}", file=sys.stderr)
    
    def load(self):
        try:
            self.index = faiss.read_index(f"{self.store_path}.faiss")
            with open(f"{self.store_path}.pkl", "rb") as f:
                self.documents = pickle.load(f)
            print(f"✅ Vector store loaded from {self.store_path}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"⚠️ Could not load vector store: {e}", file=sys.stderr)
            return False