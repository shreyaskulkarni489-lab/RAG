import os
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from app.config import settings
from app.services.embedder import embedding_service
from app.services.vector_store import vector_store_service
from app.models.chat import Conversation, Message, MessageRole

STRICT_SYSTEM_PROMPT = """You are a college information assistant. Answer the student's question using ONLY the context provided below. Do not use outside knowledge.

If the context does not contain enough information to answer, respond:
"I don't have information about that in the college documents. You may want to contact the relevant department directly."

Context:
{retrieved_chunks}

Conversation history:
{last_n_turns}

Question: {user_question}

Answer concisely, and reference which document/section supports your answer."""

FALLBACK_ANSWER = "I don't have information about that in the college documents. You may want to contact the relevant department directly."

class RAGService:
    @staticmethod
    def answer_query(
        db: Session,
        question: str,
        conversation_id: Optional[str] = None,
        department: Optional[str] = None,
        collection: Optional[str] = None,
        threshold: float = 0.65
    ) -> Dict[str, Any]:
        """
        Executes full RAG query pipeline.
        """
        # Step 1: Embed question
        q_vector = embedding_service.embed_text(question)

        # Step 2: Retrieve top-k chunks
        chunks = vector_store_service.search_similar_chunks(
            db=db,
            query_vector=q_vector,
            top_k=5,
            department=department,
            collection=collection
        )

        # Step 3: Check relevance threshold
        if not chunks or chunks[0]["relevance_score"] < threshold:
            # If top score is slightly below threshold, we still check if there's any close match
            if not chunks or chunks[0]["relevance_score"] < (threshold - 0.2):
                return {
                    "answer": FALLBACK_ANSWER,
                    "sources": [],
                    "confidence": "none",
                    "answered": False
                }

        # Step 4: Fetch conversation history if conversation_id provided
        history_text = ""
        if conversation_id:
            past_messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(6).all()
            past_messages.reverse()
            history_text = "\n".join([f"{m.role.value}: {m.content}" for m in past_messages])

        # Step 5: Format context chunks
        context_chunks_str = "\n\n".join([
            f"[Source: {c['document_title']}, Page: {c['page_number']}]\n{c['snippet']}"
            for c in chunks
        ])

        prompt = STRICT_SYSTEM_PROMPT.format(
            retrieved_chunks=context_chunks_str,
            last_n_turns=history_text if history_text else "None",
            user_question=question
        )

        # Step 6: LLM Call (OpenAI or Local heuristic generator)
        answer_text = RAGService._call_llm(prompt, question, chunks)

        return {
            "answer": answer_text,
            "sources": [
                {
                    "document_title": c["document_title"],
                    "page_number": c["page_number"],
                    "snippet": c["snippet"][:200] + "...",
                    "relevance_score": c["relevance_score"]
                }
                for c in chunks
            ],
            "confidence": "high" if chunks[0]["relevance_score"] > 0.8 else "medium",
            "answered": True
        }

    @staticmethod
    def _call_llm(prompt: str, question: str, chunks: List[Dict[str, Any]]) -> str:
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful college information assistant. Adhere strictly to provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[RAGService] OpenAI LLM call failed: {e}. Using local context extractor.")

        # Heuristic context summarizer for offline zero-key dev mode
        top_chunk = chunks[0]
        return f"Based on {top_chunk['document_title']} (Page {top_chunk['page_number']}):\n\n{top_chunk['snippet']}"

rag_service = RAGService()
