"""
Celery asynchronous task definitions for document ingestion.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.db.session import SessionLocal
from app.models.document import Document, IngestionJob
from app.services.ingestion.pipeline import ingestion_pipeline_app, update_db_job
from app.tasks.celery_app import celery_app, publish_telemetry

logger = logging.getLogger(__name__)


def run_ingestion_pipeline(
    document_id: str, task_id: str | None = None
) -> dict[str, Any]:
    """
    Core executor running the LangGraph ingestion pipeline.
    Invokable both within Celery worker and directly in tests.
    """
    logger.info("Starting ingestion execution for doc: %s", document_id)
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found in database.")

        file_path = doc.file_path
        source_mode = doc.source_mode

        # Associate Celery task ID if provided
        if task_id:
            job = (
                db.query(IngestionJob)
                .filter(IngestionJob.document_id == doc.id)
                .first()
            )
            if job:
                job.task_id = task_id
                job.status = "running"
                db.commit()

    finally:
        db.close()

    # Invoke the compiled LangGraph state machine
    try:
        initial_state = {
            "document_id": document_id,
            "source_mode": source_mode,
            "file_path": file_path,
        }
        final_state = ingestion_pipeline_app.invoke(initial_state)
        logger.info("Ingestion completed successfully for doc: %s", document_id)
        return final_state
    except Exception as exc:
        logger.exception("Ingestion failed for doc %s", document_id)
        update_db_job(
            document_id,
            step="failed",
            percent=0,
            status="failed",
            message=str(exc),
        )
        publish_telemetry(
            document_id,
            {
                "current_step": "failed",
                "percent_complete": 0,
                "status": "failed",
                "error": str(exc),
            },
        )
        raise


@celery_app.task(bind=True, name="tasks.process_document", max_retries=1)
def process_document(self, document_id: str) -> dict[str, Any]:
    """
    Asynchronous Celery task processing an uploaded academic document or book.
    """
    task_id = self.request.id if self.request else None
    return run_ingestion_pipeline(document_id=document_id, task_id=task_id)
