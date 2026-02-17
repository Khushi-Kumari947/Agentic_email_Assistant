import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import faiss
from src.config import VECTOR_STORE_PATH, EMBEDDING_MODEL

class VectorStore:
    def __init__(self):
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.documents = []  # Store original documents with metadata
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for texts"""
        embeddings = self.encoder.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def build_index(self, chunked_documents: List[Dict[str, Any]]):
        """Build FAISS index from documents"""
        texts = [doc["text"] for doc in chunked_documents]
        embeddings = self.create_embeddings(texts)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)
        
        # Store documents
        self.documents = chunked_documents
    
    def save(self, path: str = VECTOR_STORE_PATH):
        """Save index and documents to disk"""
        if self.index is None:
            raise ValueError("No index to save")
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save documents
        with open(f"{path}.pkl", "wb") as f:
            pickle.dump(self.documents, f)
    
    def load(self, path: str = VECTOR_STORE_PATH):
        """Load index and documents from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{path}.faiss")
            
            # Load documents
            with open(f"{path}.pkl", "rb") as f:
                self.documents = pickle.load(f)
            
            return True
        except:
            return False
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index is None:
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
                    "similarity_score": float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                })
        
        return results