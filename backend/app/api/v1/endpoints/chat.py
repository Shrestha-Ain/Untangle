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
    search_scope: str | None = "topic"  # "topic" | "document" | "worldwide"
    selected_node_id: str | None = None
    selected_node_name: str | None = None
    model_name: str | None = "flash"


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
        search_scope=message_in.search_scope,
        selected_node_id=message_in.selected_node_id,
        selected_node_name=message_in.selected_node_name,
        model_name=message_in.model_name,
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
    Supports topic-first scoping, document-wide RAG, and worldwide search.
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
            search_scope=data.search_scope,
            selected_node_id=data.selected_node_id,
            selected_node_name=data.selected_node_name,
            model_name=data.model_name,
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
    from app.llm.client import clean_llm_text, get_chat_model
    from app.llm.prompts import REGULUS_CHAT_PROMPT, REGULUS_SCOPED_CHAT_PROMPT
    from app.services.retrieval.local_search import execute_local_search
    from app.services.retrieval.study_features import get_node_dossier

    dossier: dict[str, Any] | None = None
    if data.selected_node_id:
        try:
            dossier = get_node_dossier(document_id, data.selected_node_id)
        except Exception as exc:
            logger.warning("Could not fetch dossier for node %s: %s", data.selected_node_id, exc)

    local_res = execute_local_search(document_id, data.query)

    is_topic_scope = (data.search_scope == "topic" or not data.search_scope) and (dossier or data.selected_node_name)

    if is_topic_scope:
        target_name = (dossier.get("name") if dossier else None) or data.selected_node_name or data.selected_node_id or "Active Concept"
        target_type = (dossier.get("type") if dossier else "CONCEPT") or "CONCEPT"
        target_desc = (dossier.get("description") if dossier else "") or ""

        rel_outs = dossier.get("outgoing_relations", []) if dossier else []
        rel_ins = dossier.get("incoming_relations", []) if dossier else []

        active_id = dossier["node_id"] if dossier else (data.selected_node_id or "node-active")
        node_ids = [active_id] + [r["target"] for r in rel_outs] + [r["source"] for r in rel_ins]
        edge_ids = [f"{r['source']}->{r['target']}" for r in rel_outs + rel_ins]

        local_context_lines = [
            f"Active Focus Tower: {target_name} ({target_type})",
            f"Definition / Purpose: {target_desc}",
            "Prerequisites & Prior Concepts:",
            *(f"- {r['source']} -[{r['relation']}]-> {target_name}" for r in rel_ins[:3]),
            "Successors & Future Dependencies:",
            *(f"- {target_name} -[{r['relation']}]-> {r['target']}" for r in rel_outs[:3]),
        ]
        local_context = "\n".join(local_context_lines)

        subgraph_lines = [
            f"- {n['name']} ({n['type']}): {n['description']}"
            for n in local_res.subgraph_nodes
            if n["id"] != active_id
        ]
        subgraph_context = "\n".join(subgraph_lines) or "No secondary peripheral nodes."

        combined_chunks = (dossier.get("text_chunks", []) if dossier else []) + local_res.text_chunks
        seen_texts: set[str] = set()
        unique_chunks: list[dict[str, Any]] = []
        for ch in combined_chunks:
            txt = ch.get("text", "")
            if txt and txt not in seen_texts:
                seen_texts.add(txt)
                unique_chunks.append(ch)

        chunks_context = "\n\n".join(
            f"[Passage {c.get('chunk_index', idx + 1)}]: {c.get('text', '')}"
            for idx, c in enumerate(unique_chunks[:4])
        ) or f"Core Syllabus Definition for {target_name}:\n{target_desc or 'Essential architectural milestone within the curriculum sequence.'}"

        prompt_messages = REGULUS_SCOPED_CHAT_PROMPT.format_messages(
            scope_mode="Topic Focus",
            target_topic=target_name,
            local_context=local_context,
            subgraph_context=subgraph_context,
            chunks_context=chunks_context,
            question=data.query,
        )
    elif data.search_scope == "worldwide":
        node_ids = [n["id"] for n in local_res.subgraph_nodes]
        edge_ids = [f"{e['source']}->{e['target']}" for e in local_res.subgraph_edges]
        target_name = data.selected_node_name or "Global Knowledge"
        prompt_messages = REGULUS_SCOPED_CHAT_PROMPT.format_messages(
            scope_mode="Worldwide AI Knowledge",
            target_topic=target_name,
            local_context=f"Subject: {target_name}. Broad worldwide literature search requested.",
            subgraph_context="Reference document concepts if applicable, but synthesize using expansive global computer science/engineering literature.",
            chunks_context="\n\n".join(
                f"[Chunk {c.get('chunk_index', idx)}]: {c.get('text', '')}"
                for idx, c in enumerate(local_res.text_chunks[:2])
            ) or f"Extensive literature and standard engineering principles apply to {target_name}.",
            question=data.query,
        )
    else:
        node_ids = [n["id"] for n in local_res.subgraph_nodes]
        edge_ids = [f"{e['source']}->{e['target']}" for e in local_res.subgraph_edges]
        subgraph_lines = [
            f"- {n['name']} ({n['type']}): {n['description']}"
            for n in local_res.subgraph_nodes
        ]
        subgraph_context = "\n".join(subgraph_lines) or "Knowledge graph topology active."
        chunks_context = "\n\n".join(
            f"[Chunk {c.get('chunk_index', idx)}]: {c['text']}"
            for idx, c in enumerate(local_res.text_chunks)
        ) or "Domain knowledge concepts active."
        prompt_messages = REGULUS_CHAT_PROMPT.format_messages(
            subgraph_context=subgraph_context,
            chunks_context=chunks_context,
            question=data.query,
        )

    try:
        model = get_chat_model(model_name=data.model_name)
        response = model.invoke(prompt_messages)
        answer_text = clean_llm_text(response.content)
    except Exception as exc:
        logger.warning("LLM fallback in query_document_direct: %s", exc)
        if is_topic_scope:
            target_name = (dossier.get("name") if dossier else None) or data.selected_node_name or "Selected Topic"
            desc = (dossier.get("description") if dossier else "") or ""
            answer_text = (
                f"🎯 **{target_name}**\n\n"
                f"💡 **Core Intuition & Analogy:**\n"
                f"{desc or 'An essential architectural milestone in this curriculum.'} "
                f"Mastering this concept ensures invariant guarantees across adjacent modules.\n\n"
                f"⚙️ **How It Works (Under the Hood):**\n"
                f"- Implements fundamental state transitions required for this domain.\n"
                f"- Exposes core interfaces utilized by successor nodes along the learning path.\n\n"
            )
            if dossier and (dossier.get("incoming_relations") or dossier.get("outgoing_relations")):
                answer_text += "🗺️ **Position in the Knowledge Town:**\n"
                for r in dossier.get("incoming_relations", [])[:2]:
                    answer_text += f"• **Prerequisite**: Builds directly upon **{r.get('source')}**\n"
                for r in dossier.get("outgoing_relations", [])[:2]:
                    answer_text += f"• **Next Progression**: Leads directly to **{r.get('target')}**\n"
                answer_text += "\n"
            if local_res.text_chunks:
                answer_text += f"📄 **Direct Source Passage:**\n\"{local_res.text_chunks[0]['text'][:260]}...\"\n\n"

            answer_text += (
                f"⚠️ **Key Exam Pitfall:**\n"
                f"Students frequently confuse the definition of {target_name} with its downstream consumers. "
                f"Be sure to distinguish between the primitive's internal mechanism and the higher-level abstraction that invokes it.\n\n"
                f"💬 **Interactive Follow-ups:**\n"
                f"👉 *\"How does this execute on modern hardware?\"*\n"
                f"👉 *\"What happens under heavy concurrency or edge cases?\"*"
            )
        elif data.search_scope == "worldwide":
            target_name = data.selected_node_name or data.query
            answer_text = (
                f"🌐 **Worldwide Engineering & AI Context for '{target_name}':**\n\n"
                f"• **Industry Standard**: In production systems at companies like Google, Meta, and the Linux kernel community, "
                f"'{target_name}' represents a critical design pattern for managing state, latency, and fault-tolerance.\n\n"
                f"• **Real-World Trade-Offs**: Engineers balance synchronization overhead against throughput, ensuring memory cache lines "
                f"and tensor pipelines stay saturated without deadlocks or race conditions.\n\n"
                f"• **Next Best Step**: Select an individual tower on the map to inspect its exact mathematical equations or system call semantics."
            )
        elif local_res.text_chunks:
            answer_text = (
                f"📄 **Document Synthesis:**\n\n"
                f"{local_res.text_chunks[0]['text'][:350]}\n\n"
                f"💡 *Select an individual tower above to dive into its step-by-step mechanism and exam traps.*"
            )
        elif local_res.subgraph_nodes:
            answer_text = (
                f"📄 **Key Document Concepts:**\n\n"
                f"The highest-yield concepts related to your query include: "
                f"**{', '.join(n['name'] for n in local_res.subgraph_nodes[:4])}**.\n\n"
                f"Select any building on the map to switch into 🎯 Topic Focus."
            )
        else:
            answer_text = (
                f"📄 **Document Synthesis for '{data.query}':**\n\n"
                f"I navigated the knowledge graph structure for this curriculum. "
                f"Connected topics along the guided learning path include {', '.join(node_ids[:3]) if node_ids else 'the foundational principles'}.\n\n"
                f"👉 *Tip: Click any tower on the town map to focus Regulus specifically on that concept!*"
            )

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
