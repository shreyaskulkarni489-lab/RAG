import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
