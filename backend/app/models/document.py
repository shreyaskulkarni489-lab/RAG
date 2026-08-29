import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class DocStatus(str, enum.Enum):
    processing = "processing"
    processed = "processed"
    failed = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    department = Column(String, nullable=True)
    collection = Column(String, nullable=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(DocStatus), default=DocStatus.processing, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    # Storing embedding as JSON or pgvector depending on DB
    embedding_json = Column(Text, nullable=False) # JSON serialized float array for universal compatibility
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
