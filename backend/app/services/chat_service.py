"""
Chat service — Session management, query routing, LangGraph/LangChain Regulus AI Guide, and token streaming.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.orm import Session

from app.llm.client import get_chat_model
from app.llm.prompts import REGULUS_CHAT_PROMPT
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatSessionCreate
from app.services.retrieval.global_search import execute_global_search
from app.services.retrieval.local_search import execute_local_search

logger = logging.getLogger(__name__)

GLOBAL_QUERY_TRIGGERS = (
    "summarize",
    "summary",
    "overview",
    "overall",
    "main themes",
    "comparison",
    "compare",
    "big picture",
    "holistic",
    "entire",
    "all chapters",
    "what is this paper about",
    "what is this book about",
)


def create_chat_session(
    db: Session, user_id: uuid.UUID, data: ChatSessionCreate
) -> ChatSession:
    """Create and persist a new chat session for a document."""
    session = ChatSession(
        user_id=user_id,
        document_id=data.document_id,
        title=data.title,
        search_mode=data.search_mode,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_chat_sessions(
    db: Session, user_id: uuid.UUID, document_id: uuid.UUID | None = None
) -> list[ChatSession]:
    """List chat sessions for a user, optionally filtered by document."""
    query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    if document_id is not None:
        query = query.filter(ChatSession.document_id == document_id)
    return query.order_by(ChatSession.updated_at.desc()).all()


def get_chat_session(
    db: Session, session_id: uuid.UUID, user_id: uuid.UUID
) -> ChatSession | None:
    """Fetch single chat session ensuring user ownership."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def get_session_messages(db: Session, session_id: uuid.UUID) -> list[ChatMessage]:
    """Fetch chronological message history for a session."""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def save_chat_message(
    db: Session,
    session_id: uuid.UUID,
    role: str,
    content: str,
    retrieved_subgraph: dict[str, Any] | None = None,
    citations: list[dict[str, Any]] | None = None,
    latency_ms: int | None = None,
) -> ChatMessage:
    """Persist a message and touch session updated_at."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        retrieved_subgraph=retrieved_subgraph,
        citations=citations,
        latency_ms=latency_ms,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def route_query(query: str, requested_mode: str | None = None) -> str:
    """
    Route search query to either 'local' or 'global'.
    - If user explicitly requested 'local' or 'global', honor it.
    - Otherwise detect thematic/holistic keywords for 'global', default to 'local'.
    """
    if requested_mode in ("local", "global"):
        return requested_mode

    q_lower = query.lower()
    if any(trigger in q_lower for trigger in GLOBAL_QUERY_TRIGGERS):
        return "global"

    return "local"


async def stream_chat_turn(
    db: Session,
    session: ChatSession,
    query: str,
    search_mode: str | None = None,
) -> AsyncGenerator[dict[str, Any]]:
    """
    Stream Regulus AI Guide conversation turn:
    1. Persist user message
    2. Route query (local vs global)
    3. Retrieve grounding subgraph & chunks
    4. Stream LLM tokens
    5. Persist assistant message with citations & illuminated subgraph
    6. Yield completion event
    """
    start_time = time.time()

    # 1. Save user query
    save_chat_message(db, session.id, role="user", content=query)

    # 2. Route search
    mode = route_query(query, search_mode or session.search_mode)

    # 3. Retrieve grounding context
    node_ids: list[str] = []
    edge_ids: list[str] = []
    citations: list[dict[str, Any]] = []
    subgraph_context: str = ""
    chunks_context: str = ""

    doc_id_str = str(session.document_id)

    if mode == "local":
        local_res = execute_local_search(doc_id_str, query)
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

        citations = [
            {
                "chunk_id": str(c.get("chunk_index", idx)),
                "text": c.get("text", "")[:140],
                "page_number": c.get("page_number"),
            }
            for idx, c in enumerate(local_res.text_chunks)
        ]

    else:
        global_res = execute_global_search(doc_id_str, query)
        node_ids = [c["title"] for c in global_res.communities_used]
        edge_ids = []

        subgraph_lines = [
            f"### {c['title']} (Rating: {c['rating']})\n{c['summary']}"
            for c in global_res.communities_used
        ]
        subgraph_context = "\n\n".join(subgraph_lines) or "No community clusters found."

        chunk_lines = [f"- {f}" for f in global_res.key_findings]
        chunks_context = "\n".join(chunk_lines) or "No high-level findings found."

        citations = [
            {
                "chunk_id": f"comm-{c['id']}",
                "text": c.get("summary", "")[:140],
                "page_number": None,
            }
            for c in global_res.communities_used
        ]

    # 4. Stream response via LangChain
    prompt_messages = REGULUS_CHAT_PROMPT.format_messages(
        subgraph_context=subgraph_context,
        chunks_context=chunks_context,
        question=query,
    )

    full_response_text: list[str] = []

    try:
        model = get_chat_model()
        async for chunk in model.astream(prompt_messages):
            token = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
            if token:
                full_response_text.append(token)
                yield {"type": "token", "content": token}
    except (ValueError, RuntimeError, OSError) as exc:
        logger.warning("Regulus streaming fallback: %s", exc)
        if mode == "local" and local_res.text_chunks:
            fallback_text = f"Based on the text: {local_res.text_chunks[0]['text'][:300]}"
        elif mode == "global" and global_res.communities_used:
            fallback_text = f"Summary: {global_res.communities_used[0]['summary']}"
        else:
            fallback_text = "I could not locate direct references in the document for this question."

        full_response_text.append(fallback_text)
        yield {"type": "token", "content": fallback_text}

    latency_ms = int((time.time() - start_time) * 1000)
    complete_answer = "".join(full_response_text)

    # 5. Persist assistant reply
    save_chat_message(
        db,
        session.id,
        role="assistant",
        content=complete_answer,
        retrieved_subgraph={"nodes": node_ids, "edges": edge_ids},
        citations=citations,
        latency_ms=latency_ms,
    )

    # 6. Emit done event
    yield {
        "type": "done",
        "citations": citations,
        "subgraph": {"node_ids": node_ids, "edge_ids": edge_ids},
        "search_mode": mode,
        "latency_ms": latency_ms,
    }


def generate_chat_turn_sync(
    db: Session,
    session: ChatSession,
    query: str,
    search_mode: str | None = None,
) -> ChatMessage:
    """Synchronous fallback for HTTP REST endpoints."""
    start_time = time.time()
    save_chat_message(db, session.id, role="user", content=query)
    mode = route_query(query, search_mode or session.search_mode)

    doc_id_str = str(session.document_id)
    node_ids: list[str] = []
    edge_ids: list[str] = []
    citations: list[dict[str, Any]] = []

    if mode == "local":
        local_res = execute_local_search(doc_id_str, query)
        node_ids = [n["id"] for n in local_res.subgraph_nodes]
        edge_ids = [f"{e['source']}->{e['target']}" for e in local_res.subgraph_edges]
        subgraph_context = "\n".join(
            f"- {n['name']} ({n['type']}): {n['description']}"
            for n in local_res.subgraph_nodes
        )
        chunks_context = "\n\n".join(
            f"[Chunk {c.get('chunk_index', idx)}]: {c['text']}"
            for idx, c in enumerate(local_res.text_chunks)
        )
        citations = [
            {
                "chunk_id": str(c.get("chunk_index", idx)),
                "text": c.get("text", "")[:140],
                "page_number": c.get("page_number"),
            }
            for idx, c in enumerate(local_res.text_chunks)
        ]
    else:
        global_res = execute_global_search(doc_id_str, query)
        node_ids = [c["title"] for c in global_res.communities_used]
        edge_ids = []
        subgraph_context = "\n\n".join(
            f"### {c['title']} (Rating: {c['rating']})\n{c['summary']}"
            for c in global_res.communities_used
        )
        chunks_context = "\n".join(f"- {f}" for f in global_res.key_findings)
        citations = [
            {
                "chunk_id": f"comm-{c['id']}",
                "text": c.get("summary", "")[:140],
                "page_number": None,
            }
            for c in global_res.communities_used
        ]

    prompt_messages = REGULUS_CHAT_PROMPT.format_messages(
        subgraph_context=subgraph_context,
        chunks_context=chunks_context,
        question=query,
    )

    try:
        model = get_chat_model()
        response = model.invoke(prompt_messages)
        answer = str(response.content)
    except (ValueError, RuntimeError, OSError) as exc:
        logger.warning("Regulus sync chat fallback: %s", exc)
        answer = "I was unable to synthesize a response from the document."

    latency_ms = int((time.time() - start_time) * 1000)

    return save_chat_message(
        db,
        session.id,
        role="assistant",
        content=answer,
        retrieved_subgraph={"nodes": node_ids, "edges": edge_ids},
        citations=citations,
        latency_ms=latency_ms,
    )
