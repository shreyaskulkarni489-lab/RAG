import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class FeedbackEnum(str, enum.Enum):
    up = "up"
    down = "down"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True) # JSON serialized list of sources
    feedback = Column(Enum(FeedbackEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
