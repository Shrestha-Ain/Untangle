"""
Document, DocumentLink, and IngestionJob ORM models.

Supports both Research Mode (academic literature) and Study Mode (textbooks),
cross-source linking, and Celery asynchronous ingestion tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.chat import ChatSession
    from app.models.user import User


class Document(Base):
    """
    Ingested document record.

    Contains metadata, source mode (research vs study), ingestion status,
    and aggregate knowledge graph realm statistics.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_mode: Mapped[str] = mapped_column(
        String(32), nullable=False, default="research"
    )  # "research" | "study"
    display_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # "pending" | "parsing" | "chunking" | "extracting" | "deduping" | "clustering" | "summarizing" | "ready" | "failed"
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "chunk_count": 0,
            "entity_count": 0,
            "community_count": 0,
            "chapter_count": 0,
        },
    )
    created_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="documents")
    links_as_source: Mapped[list[DocumentLink]] = relationship(
        "DocumentLink",
        foreign_keys="DocumentLink.source_document_id",
        back_populates="source_document",
        cascade="all, delete-orphan",
    )
    links_as_target: Mapped[list[DocumentLink]] = relationship(
        "DocumentLink",
        foreign_keys="DocumentLink.target_document_id",
        back_populates="target_document",
        cascade="all, delete-orphan",
    )
    ingestion_jobs: Mapped[list[IngestionJob]] = relationship(
        "IngestionJob", back_populates="document", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list[ChatSession]] = relationship(
        "ChatSession", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document {self.display_title or self.filename} ({self.status})>"


class DocumentLink(Base):
    """
    Cross-source conceptual link between two documents.

    Surfaces prerequisites and connections (e.g. a topic in a textbook
    links to a deep-dive research paper).
    """

    __tablename__ = "document_links"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    link_mode: Mapped[str] = mapped_column(
        String(32), nullable=False, default="auto"
    )  # "auto" | "manual"
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="suggested"
    )  # "suggested" | "accepted" | "rejected"
    created_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    source_document: Mapped[Document] = relationship(
        "Document",
        foreign_keys=[source_document_id],
        back_populates="links_as_source",
    )
    target_document: Mapped[Document] = relationship(
        "Document",
        foreign_keys=[target_document_id],
        back_populates="links_as_target",
    )


class IngestionJob(Base):
    """
    Async ingestion telemetry tracking.

    Used by the Celery worker to report live progress to Redis and PostgreSQL.
    """

    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # "pending" | "running" | "completed" | "failed"
    current_step: Mapped[str] = mapped_column(
        String(32), nullable=False, default="parse"
    )  # "parse" | "chunk" | "extract" | "dedup" | "cluster" | "summarize" | "done"
    percent_complete: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    towers_built: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    roads_laid: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Any] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    document: Mapped[Document] = relationship(
        "Document", back_populates="ingestion_jobs"
    )
