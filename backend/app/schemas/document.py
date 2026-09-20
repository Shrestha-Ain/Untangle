"""
Pydantic schemas for Document, DocumentLink, and IngestionJob.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentStats(BaseModel):
    """Aggregate statistics for an ingested document's knowledge realm."""

    chunk_count: int = 0
    entity_count: int = 0
    community_count: int = 0
    chapter_count: int = 0


class DocumentBase(BaseModel):
    filename: str
    source_mode: str = Field(
        default="research", description="Mode: 'research' (papers) or 'study' (textbooks)"
    )
    display_title: str | None = None


class DocumentCreate(DocumentBase):
    file_path: str
    file_size: int = 0


class DocumentUpdate(BaseModel):
    display_title: str | None = None
    status: str | None = None
    error_message: str | None = None
    stats: dict[str, Any] | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    file_size: int
    status: str
    error_message: str | None = None
    stats: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DocumentLinkBase(BaseModel):
    source_document_id: uuid.UUID
    target_document_id: uuid.UUID
    topic_id: str | None = None
    link_reason: str | None = None
    link_mode: str = "auto"
    status: str = "suggested"


class DocumentLinkCreate(DocumentLinkBase):
    pass


class DocumentLinkRead(DocumentLinkBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class IngestionJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    task_id: str | None = None
    status: str
    current_step: str
    percent_complete: int
    message: str | None = None
    towers_built: int = 0
    roads_laid: int = 0
    created_at: datetime
    updated_at: datetime

