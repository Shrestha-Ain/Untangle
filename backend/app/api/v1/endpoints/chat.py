"""
Chat REST API endpoints.

Endpoints:
- POST /chat/sessions                  — create a new conversation session
- GET  /chat/sessions                  — list user's conversation sessions
- GET  /chat/sessions/{id}             — get session metadata
- GET  /chat/sessions/{id}/messages    — get chronological message history
- POST /chat/sessions/{id}/messages    — sync fallback to send user message
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageRead,
    ChatSessionCreate,
    ChatSessionRead,
)
from app.services import chat_service, document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/sessions", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED
)
def create_session(
    data: ChatSessionCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Initialize a new Regulus chat session linked to a document.
    """
    # Verify document exists and belongs to user
    doc = document_service.get_document_by_id(
        db=db, document_id=data.document_id, user_id=current_user.id
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referenced document not found",
        )

    session = chat_service.create_chat_session(
        db=db, user_id=current_user.id, data=data
    )
    return session


@router.get("/sessions", response_model=list[ChatSessionRead])
def list_sessions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    document_id: Annotated[uuid.UUID | None, Query()] = None,
):
    """
    List all chat sessions for the current user, optionally filtered by document_id.
    """
    return chat_service.list_sessions(
        db=db, user_id=current_user.id, document_id=document_id
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionRead)
def get_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve metadata for a specific chat session.
    """
    session = chat_service.get_chat_session(
        db=db, session_id=session_id, user_id=current_user.id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return session


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def get_session_messages(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve message history for a chat session.
    """
    session = chat_service.get_chat_session(
        db=db, session_id=session_id, user_id=current_user.id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return chat_service.get_session_messages(db=db, session_id=session_id)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def send_message_sync(
    session_id: uuid.UUID,
    message_in: ChatMessageCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Synchronous fallback endpoint to ask a question in a chat session.
    For streaming responses with token-by-token illumination, use the WebSocket endpoint instead.
    """
    session = chat_service.get_chat_session(
        db=db, session_id=session_id, user_id=current_user.id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    assistant_msg = chat_service.generate_chat_turn_sync(
        db=db,
        session=session,
        query=message_in.content,
        search_mode=message_in.search_mode,
    )
    return assistant_msg
