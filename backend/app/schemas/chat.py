from pydantic import BaseModel
from typing import Optional, List

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    question: str
    collection: Optional[str] = None
    department: Optional[str] = None

class SourceMetadata(BaseModel):
    document_title: str
    page_number: Optional[int] = None
    snippet: str
    relevance_score: float

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[SourceMetadata]
    confidence: str
    answered: bool
