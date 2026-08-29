import json
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

class VectorStoreService:
    @staticmethod
    def search_similar_chunks(
        db: Session,
        query_vector: List[float],
        top_k: int = 5,
        department: Optional[str] = None,
        collection: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant chunks using cosine similarity across chunks.
        Supports filtering by department and collection.
        """
        # Query chunks joining with Document metadata
        query = db.query(DocumentChunk, Document).join(Document, DocumentChunk.document_id == Document.id)

        if department:
            query = query.filter(Document.department == department)
        if collection:
            query = query.filter(Document.collection == collection)

        results = query.all()
        if not results:
            return []

        scored_chunks = []
        for chunk, doc in results:
            try:
                emb = json.loads(chunk.embedding_json)
                score = cosine_similarity(query_vector, emb)
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "page_number": chunk.page_number,
                    "snippet": chunk.chunk_text,
                    "relevance_score": round(score, 4)
                })
            except Exception as e:
                continue

        # Sort by relevance_score descending
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:top_k]

vector_store_service = VectorStoreService()
