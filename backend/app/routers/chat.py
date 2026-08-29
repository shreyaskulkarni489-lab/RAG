import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.chat import Conversation, Message, MessageRole, FeedbackEnum
from app.schemas.chat import ChatMessageRequest, ChatResponse
from app.security.jwt import get_current_user
from app.services.rag import rag_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
def send_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retrieve or create conversation
    conv_id = payload.conversation_id
    if not conv_id:
        title = payload.question[:40] + ("..." if len(payload.question) > 40 else "")
        conv = Conversation(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            title=title
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id
    else:
        conv = db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Record user message
    user_msg = Message(
        conversation_id=conv_id,
        role=MessageRole.user,
        content=payload.question
    )
    db.add(user_msg)
    db.commit()

    # RAG pipeline execution
    rag_result = rag_service.answer_query(
        db=db,
        question=payload.question,
        conversation_id=conv_id,
        department=payload.department,
        collection=payload.collection
    )

    # Record assistant message
    asst_msg = Message(
        conversation_id=conv_id,
        role=MessageRole.assistant,
        content=rag_result["answer"],
        sources_json=json.dumps(rag_result["sources"])
    )
    db.add(asst_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conv_id,
        answer=rag_result["answer"],
        sources=rag_result["sources"],
        confidence=rag_result["confidence"],
        answered=rag_result["answered"]
    )

@router.get("/conversations")
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat()
        }
        for c in conversations
    ]

@router.get("/conversations/{conversation_id}")
def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "sources": json.loads(m.sources_json) if m.sources_json else [],
                "feedback": m.feedback.value if m.feedback else None,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }

@router.post("/message/{message_id}/feedback")
def submit_feedback(
    message_id: str,
    feedback: str, # "up" or "down"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if feedback.lower() == "up":
        msg.feedback = FeedbackEnum.up
    elif feedback.lower() == "down":
        msg.feedback = FeedbackEnum.down
    else:
        raise HTTPException(status_code=400, detail="Invalid feedback option")

    db.commit()
    return {"status": "success", "message_id": message_id, "feedback": msg.feedback.value}
