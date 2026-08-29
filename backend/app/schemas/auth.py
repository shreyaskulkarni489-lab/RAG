from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from typing import Optional

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    name: str

class TokenPayload(BaseModel):
    sub: str
    role: str

