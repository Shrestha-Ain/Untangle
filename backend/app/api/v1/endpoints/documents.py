"""
Document management endpoints.

- POST   /documents/upload  — upload PDF/TXT/MD, validate, save, create Document row
- GET    /documents         — list user's documents
- GET    /documents/{id}    — retrieve document status and realm stats
- DELETE /documents/{id}    — cascade delete document, file, vectors, and graph nodes
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services import document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def upload_document(
    file: Annotated[UploadFile, File(description="PDF, Markdown, or plain text file")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    source_mode: Annotated[
        str, Form(description="'research' for academic papers, 'study' for textbooks")
    ] = "research",
    display_title: Annotated[
        str | None, Form(description="Optional custom display title")
    ] = None,
):
    """
    Upload and register a document for Knowledge Graph ingestion.

    Validates file format (.pdf, .txt, .md), enforces size limits (<=50MB),
    saves to isolated user storage, and creates initial ingestion tracking state.
    """
    if source_mode not in ("research", "study"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source_mode. Must be 'research' or 'study'.",
        )

    try:
        saved_path, file_size = document_service.save_upload_file(current_user.id, file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    doc = document_service.create_document(
        db=db,
        user_id=current_user.id,
        filename=file.filename or "uploaded_file",
        file_path=saved_path,
        file_size=file_size,
        source_mode=source_mode,
        display_title=display_title,
    )

    # Dispatch Celery asynchronous ingestion pipeline
    try:
        import redis
        from celery.exceptions import CeleryError

        from app.tasks.ingestion import process_document

        process_document.delay(str(doc.id))
        logger.info("Enqueued Celery ingestion task for doc %s", doc.id)
    except (CeleryError, redis.RedisError, OSError, RuntimeError) as exc:
        logger.warning(
            "Celery dispatch deferred (worker/Redis offline in dev): %s", exc
        )

    return doc


@router.get("", response_model=list[DocumentRead])
def list_documents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    List all documents in the user's library with realm statistics and processing status.
    """
    return document_service.list_documents_for_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Retrieve document metadata, current ingestion step, and knowledge realm statistics.
    """
    doc = document_service.get_document_by_id(
        db=db, document_id=document_id, user_id=current_user.id
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Cascade delete a document from database, disk storage, vector index, and knowledge graph.
    """
    deleted = document_service.delete_document(
        db=db, document_id=document_id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return {"status": "deleted", "id": str(document_id)}
