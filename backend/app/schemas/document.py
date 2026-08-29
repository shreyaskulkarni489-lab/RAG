from pydantic import BaseModel
from typing import Optional

class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    department: Optional[str] = None
    collection: Optional[str] = None
    status: str
    version: int
    created_at: str

    class Config:
        from_attributes = True

