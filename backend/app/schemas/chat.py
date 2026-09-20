"""
Pydantic schemas for ChatSession, ChatMessage, and streaming events.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageBase(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)
    search_mode: str | None = Field(
        default=None, description="Optional override: 'local', 'global', or 'auto'"
    )


class ChatMessageRead(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    retrieved_subgraph: dict[str, Any] | None = None
    citations: list[dict[str, Any]] | None = None
    latency_ms: int | None = None
    created_at: datetime


class ChatSessionBase(BaseModel):
    title: str = "New Conversation"
    search_mode: str = Field(
        default="auto", description="'local' (entity), 'global' (community), or 'auto'"
    )


class ChatSessionCreate(ChatSessionBase):
    document_id: uuid.UUID


class ChatSessionUpdate(BaseModel):
    title: str | None = None
    search_mode: str | None = None


class ChatSessionRead(ChatSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageRead] = []


class SubgraphData(BaseModel):
    node_ids: list[str] = []
    edge_ids: list[str] = []


class CitationItem(BaseModel):
    chunk_id: str
    text: str
    page_number: int | None = None


class ChatStreamTokenEvent(BaseModel):
    type: str = "token"
    content: str


class ChatStreamDoneEvent(BaseModel):
    type: str = "done"
    citations: list[CitationItem] = []
    subgraph: SubgraphData = Field(default_factory=SubgraphData)
    search_mode: str = "local"
    latency_ms: int = 0


class ChatStreamErrorEvent(BaseModel):
    type: str = "error"
    message: str

