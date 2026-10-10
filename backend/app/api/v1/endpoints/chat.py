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
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_user_optional
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


class DirectQueryRequest(BaseModel):
    query: str
    search_mode: str | None = "auto"


class DirectQueryResponse(BaseModel):
    answer: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    subgraph: dict[str, list[str]] = Field(default_factory=dict)
    suggested_sources: list[dict[str, Any]] = Field(default_factory=list)


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
    return chat_service.list_chat_sessions(
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


@router.post(
    "/sessions/{document_id}/query",
    response_model=DirectQueryResponse,
)
def query_document_direct(
    document_id: str,
    data: DirectQueryRequest,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Direct conversational query endpoint for Regulus AI Guide.
    Finds or creates a chat session for this document and generates a grounded response.
    """
    doc_uuid: uuid.UUID | None = None
    session: chat_service.ChatSession | None = None

    if current_user:
        try:
            doc_uuid = uuid.UUID(document_id)
            doc = document_service.get_document_by_id(
                db=db, document_id=doc_uuid, user_id=current_user.id
            )
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found",
                )
        except ValueError:
            # Non-UUID mock/demo document identifier
            pass

        if doc_uuid:
            sessions = chat_service.list_chat_sessions(
                db=db, user_id=current_user.id, document_id=doc_uuid
            )
            if sessions:
                session = sessions[0]
            else:
                session = chat_service.create_chat_session(
                    db=db,
                    user_id=current_user.id,
                    data=ChatSessionCreate(
                        document_id=doc_uuid,
                        title="Regulus Chat",
                        search_mode=data.search_mode or "auto",
                    ),
                )

    if session:
        msg = chat_service.generate_chat_turn_sync(
            db=db,
            session=session,
            query=data.query,
            search_mode=data.search_mode,
        )
        node_ids: list[str] = []
        edge_ids: list[str] = []
        if msg.retrieved_subgraph:
            node_ids = msg.retrieved_subgraph.get("nodes", [])
            edge_ids = msg.retrieved_subgraph.get("edges", [])

        citations_list: list[dict[str, Any]] = []
        if msg.citations:
            for idx, c in enumerate(msg.citations):
                citations_list.append(
                    {
                        "document_id": document_id,
                        "chunk_id": str(c.get("chunk_id", idx)),
                        "title": f"Page {c.get('page_number')}" if c.get("page_number") else "Document Citation",
                        "snippet": c.get("text", ""),
                    }
                )

        return DirectQueryResponse(
            answer=msg.content,
            citations=citations_list,
            subgraph={"nodeIds": node_ids, "edgeIds": edge_ids},
            suggested_sources=[],
        )

    # Direct query execution for seeded / demo document graphs
    from app.llm.client import get_chat_model
    from app.llm.prompts import REGULUS_CHAT_PROMPT
    from app.services.retrieval.local_search import execute_local_search

    local_res = execute_local_search(document_id, data.query)
    node_ids = [n["id"] for n in local_res.subgraph_nodes]
    edge_ids = [f"{e['source']}->{e['target']}" for e in local_res.subgraph_edges]

    subgraph_lines = [
        f"- {n['name']} ({n['type']}): {n['description']}"
        for n in local_res.subgraph_nodes
    ]
    subgraph_context = "\n".join(subgraph_lines) or "No specific subgraph nodes found."

    chunk_lines = [
        f"[Chunk {c.get('chunk_index', idx)}]: {c['text']}"
        for idx, c in enumerate(local_res.text_chunks)
    ]
    chunks_context = "\n\n".join(chunk_lines) or "No verbatim chunks found."

    prompt_messages = REGULUS_CHAT_PROMPT.format_messages(
        subgraph_context=subgraph_context,
        chunks_context=chunks_context,
        question=data.query,
    )

    try:
        model = get_chat_model()
        response = model.invoke(prompt_messages)
        answer_text = (
            response.content if isinstance(response.content, str) else str(response.content)
        )
    except Exception as exc:
        logger.warning("LLM fallback in query_document_direct: %s", exc)
        if local_res.text_chunks:
            answer_text = f"Based on the document passages:\n\n{local_res.text_chunks[0]['text'][:350]}"
        elif local_res.subgraph_nodes:
            answer_text = f"Key concepts related to your query include: {', '.join(n['name'] for n in local_res.subgraph_nodes[:4])}."
        else:
            answer_text = f"I explored the knowledge graph for '{data.query}'. Connected concepts along the learning path include {', '.join(node_ids[:3]) if node_ids else 'the foundational topics'}."

    citations_list = [
        {
            "document_id": document_id,
            "chunk_id": str(c.get("chunk_index", idx)),
            "title": f"Source Passage {idx + 1}",
            "snippet": c.get("text", "")[:150],
        }
        for idx, c in enumerate(local_res.text_chunks)
    ]

    return DirectQueryResponse(
        answer=answer_text,
        citations=citations_list,
        subgraph={"nodeIds": node_ids, "edgeIds": edge_ids},
        suggested_sources=[],
    )
