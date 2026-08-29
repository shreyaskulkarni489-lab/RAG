import os
import json
import uuid
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.document import Document, DocumentChunk, DocStatus
from app.schemas.document import DocumentResponse
from app.security.jwt import require_admin
from app.services.parser import DocumentParser
from app.services.chunker import RecursiveChunker
from app.services.embedder import embedding_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    collection: Optional[str] = Form(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Save uploaded file
    file_id = str(uuid.uuid4())
    filename = file.filename
    doc_title = title if title else filename
    saved_filename = f"{file_id}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    doc = Document(
        id=file_id,
        title=doc_title,
        filename=filename,
        file_path=file_path,
        department=department,
        collection=collection,
        uploaded_by=current_user.id,
        status=DocStatus.processing,
        version=1
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # Step 1: Parse
        pages = DocumentParser.parse_file(file_path)

        # Step 2: Chunk
        chunker = RecursiveChunker()
        chunks = chunker.chunk_pages(pages)

        # Step 3: Embed & Store
        texts_to_embed = [c["chunk_text"] for c in chunks]
        embeddings = embedding_service.embed_batch(texts_to_embed)

        for chunk_data, emb in zip(chunks, embeddings):
            chunk_obj = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                chunk_text=chunk_data["chunk_text"],
                chunk_index=chunk_data["chunk_index"],
                page_number=chunk_data["page_number"],
                embedding_json=json.dumps(emb)
            )
            db.add(chunk_obj)

        doc.status = DocStatus.processed
        db.commit()
        db.refresh(doc)

    except Exception as e:
        print(f"[Admin Router] Document processing error: {e}")
        doc.status = DocStatus.failed
        db.commit()
        db.refresh(doc)

    status_str = doc.status.value if hasattr(doc.status, "value") else str(doc.status)
    return DocumentResponse(
        id=str(doc.id),
        title=doc.title,
        filename=doc.filename,
        department=doc.department,
        collection=doc.collection,
        status=status_str,
        version=doc.version,
        created_at=doc.created_at.isoformat()
    )

@router.get("/documents")
def list_documents(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "filename": d.filename,
            "department": d.department,
            "collection": d.collection,
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "version": d.version,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete chunks
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    # Delete file from disk if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"status": "success", "message": "Document and associated chunks deleted"}
