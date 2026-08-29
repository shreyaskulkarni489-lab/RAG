import os
import json
import numpy as np
from typing import List
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.use_local = settings.USE_LOCAL_EMBEDDINGS
        self.local_model = None

        if self.use_local and not settings.OPENAI_API_KEY:
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            except Exception as e:
                print(f"[EmbeddingService] Warning: Could not load sentence-transformers: {e}. Using deterministic fallback embedder.")

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # If OpenAI key provided and not forced to local
        if settings.OPENAI_API_KEY and not self.use_local:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                return [d.embedding for d in response.data]
            except Exception as e:
                print(f"[EmbeddingService] OpenAI embedding error: {e}. Falling back to local/deterministic.")

        # Fallback to local sentence-transformers if available
        if self.local_model:
            embeddings = self.local_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

        # Deterministic lightweight TF-IDF-like / hashing vector fallback for offline zero-dependency run
        return [self._generate_deterministic_vector(t) for t in texts]

    def _generate_deterministic_vector(self, text: str, dim: int = 384) -> List[float]:
        """Generates a normalized deterministic embedding vector based on word hash n-grams for local testing without external libraries."""
        words = text.lower().split()
        vec = np.zeros(dim, dtype=np.float32)
        if not words:
            return vec.tolist()

        for w in words:
            idx = abs(hash(w)) % dim
            vec[idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

embedding_service = EmbeddingService()
