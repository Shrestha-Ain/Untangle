"""
Document management service — handling upload file storage, database records, and cascade deletion.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path

import httpx
from fastapi import UploadFile
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document, IngestionJob

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def save_upload_file(user_id: uuid.UUID, upload_file: UploadFile) -> tuple[str, int]:
    """
    Save an uploaded file to the user's isolated directory within the configured upload_dir.
    Returns (saved_file_path, file_size_bytes).
    """
    settings = get_settings()
    upload_root = Path(settings.upload_dir)
    user_dir = upload_root / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    original_filename = upload_file.filename or "uploaded_document"
    ext = Path(original_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Sanitize and create unique disk name to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{Path(original_filename).name}"
    target_path = user_dir / unique_filename

    # Stream write to disk
    file_size = 0
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        file_size = buffer.tell()

    if file_size > MAX_FILE_SIZE:
        # Delete the oversized file immediately
        if target_path.exists():
            target_path.unlink()
        raise ValueError(
            f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds 50MB limit."
        )

    logger.info("Saved upload for user %s: %s (%d bytes)", user_id, target_path, file_size)
    return str(target_path), file_size


def create_document(
    db: Session,
    user_id: uuid.UUID,
    filename: str,
    file_path: str,
    file_size: int,
    source_mode: str = "research",
    display_title: str | None = None,
) -> Document:
    """
    Create a new Document record and an initial IngestionJob telemetry row.
    """
    doc = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        source_mode=source_mode,
        display_title=display_title or filename,
        status="pending",
        stats={
            "chunk_count": 0,
            "entity_count": 0,
            "community_count": 0,
            "chapter_count": 0,
        },
    )
    db.add(doc)
    db.flush()

    job = IngestionJob(
        document_id=doc.id,
        status="pending",
        current_step="parse",
        percent_complete=0,
        message="Queued for processing",
    )
    db.add(job)
    db.commit()
    db.refresh(doc)
    logger.info("Created document %s ('%s')", doc.id, doc.display_title)
    return doc


def get_document_by_id(
    db: Session, document_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> Document | None:
    """Retrieve document by ID, optionally enforcing user ownership."""
    query = db.query(Document).filter(Document.id == document_id)
    if user_id is not None:
        query = query.filter(Document.user_id == user_id)
    return query.first()


def list_documents_for_user(
    db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> list[Document]:
    """List documents owned by user, ordered by latest updated."""
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_document(
    db: Session, document_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    """
    Cascade delete a document:
    1. Removes database record (cascades to links, jobs, chat sessions)
    2. Deletes physical file from disk
    3. Cleans up any Qdrant points and Neo4j graph nodes
    """
    doc = get_document_by_id(db, document_id, user_id=user_id)
    if not doc:
        return False

    file_path = doc.file_path
    db.delete(doc)
    db.commit()

    # Remove file on disk
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info("Deleted file on disk: %s", file_path)
    except OSError as exc:
        logger.warning("Could not delete file %s: %s", file_path, exc)

    # Clean up Qdrant points
    try:
        from qdrant_client.http.exceptions import ApiException
        from qdrant_client.http.models import FieldCondition, Filter, MatchValue

        from app.db.qdrant import (
            CHUNKS_COLLECTION,
            ENTITIES_COLLECTION,
            TOPICS_COLLECTION,
            get_qdrant_client,
        )

        qdrant = get_qdrant_client()
        doc_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))]
        )
        for col in (CHUNKS_COLLECTION, ENTITIES_COLLECTION, TOPICS_COLLECTION):
            qdrant.delete(collection_name=col, points_selector=doc_filter)
    except (ApiException, httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:
        logger.debug("Qdrant cleanup skipped/deferred: %s", exc)

    # Clean up Neo4j nodes
    try:
        from app.db.neo4j import get_neo4j_driver

        driver = get_neo4j_driver()
        with driver.session() as session:
            session.run(
                "MATCH (n {document_id: $doc_id}) DETACH DELETE n",
                doc_id=str(document_id),
            )
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        logger.debug("Neo4j cleanup skipped/deferred: %s", exc)

    return True

