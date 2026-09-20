"""
Qdrant vector database client provider and collection initializers.

Houses dense vector indexes for:
1. `chunks`: Document text chunks for semantic retrieval
2. `entities`: Named entities for local search seed discovery & deduplication
3. `topics`: Study mode topics for cross-source prerequisites discovery
"""

from __future__ import annotations

import logging

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PayloadSchemaType, VectorParams

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_qdrant_client: QdrantClient | None = None

CHUNKS_COLLECTION = "chunks"
ENTITIES_COLLECTION = "entities"
TOPICS_COLLECTION = "topics"


def get_qdrant_client() -> QdrantClient:
    """Lazy singleton for the Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        settings = get_settings()
        logger.info("Initializing Qdrant client at %s", settings.qdrant_url)
        _qdrant_client = QdrantClient(url=settings.qdrant_url)
    return _qdrant_client


def close_qdrant_client() -> None:
    """Closes the Qdrant client connection."""
    global _qdrant_client
    if _qdrant_client is not None:
        try:
            _qdrant_client.close()
        except (httpx.HTTPError, OSError):
            pass
        _qdrant_client = None


def init_qdrant_collections(
    client: QdrantClient | None = None,
    dim: int | None = None,
) -> None:
    """
    Ensures all required Qdrant collections and payload indexes exist.
    """
    settings = get_settings()
    dimension = dim or settings.embedding_dim

    if client is None:
        try:
            client = get_qdrant_client()
            # Verify connectivity
            client.get_collections()
        except (httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:
            logger.warning(
                "Qdrant connectivity check deferred (Qdrant not reachable yet): %s", exc
            )
            return

    collections = [CHUNKS_COLLECTION, ENTITIES_COLLECTION, TOPICS_COLLECTION]

    for col in collections:
        try:
            if not client.collection_exists(collection_name=col):
                logger.info("Creating Qdrant collection: %s (dim=%d)", col, dimension)
                client.create_collection(
                    collection_name=col,
                    vectors_config=VectorParams(
                        size=dimension, distance=Distance.COSINE
                    ),
                )
                # Index document_id for fast filtered retrieval
                client.create_payload_index(
                    collection_name=col,
                    field_name="document_id",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
        except (httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:
            logger.warning("Failed to initialize collection '%s': %s", col, exc)
