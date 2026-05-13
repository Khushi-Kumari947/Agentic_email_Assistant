import sys
from sentence_transformers import SentenceTransformer
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

        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

        self.index = self.pc.Index(PINECONE_INDEX_NAME)

        print(
            "✅ Pinecone initialized",
            file=sys.stderr
        )

    @property
    def encoder(self):
        """
        Lazy-load embedding model only when needed.
        """

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
        """
        Generate embeddings for given texts.
        """

        return self.encoder.encode(
            texts,
            convert_to_numpy=True
        )

    def build_index(self, chunked_docs):
        """
        Generate embeddings and upload to Pinecone.
        """

        print(
            "🗑 Clearing old Pinecone vectors...",
            file=sys.stderr
        )

        # Delete previous vectors
        self.index.delete(delete_all=True)

        print(
            f"🔨 Uploading {len(chunked_docs)} chunks to Pinecone...",
            file=sys.stderr
        )

        texts = [doc["text"] for doc in chunked_docs]

        embeddings = self.create_embeddings(texts)

        vectors = []

        for i, (embedding, doc) in enumerate(
            zip(embeddings, chunked_docs)
        ):
            vectors.append({
                "id": str(i),
                "values": embedding.tolist(),
                "metadata": {
                    "text": doc["text"]
                }
            })

        # Upload vectors to Pinecone
        self.index.upsert(vectors=vectors)

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

        query_embedding = self.create_embeddings([query])

        results = self.index.query(
            vector=query_embedding.tolist()[0],
            top_k=k,
            include_metadata=True
        )

        formatted_results = []

        for match in results["matches"]:
            formatted_results.append({
                "document": {
                    "text": match["metadata"]["text"]
                },
                "similarity_score": float(match["score"])
            })

        print(
            f"✅ Retrieved {len(formatted_results)} matching documents",
            file=sys.stderr
        )

        return formatted_results