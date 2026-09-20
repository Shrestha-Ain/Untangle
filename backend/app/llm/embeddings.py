"""
Local dense vector embedding service using FastEmbed.

Executes ONNX-quantized BAAI/bge-small-en-v1.5 locally on CPU.
Zero external API costs, ~10ms per batch, generating 384-dimensional vectors.
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
from fastembed import TextEmbedding

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_embedding_service: FastEmbedService | None = None


class FastEmbedService:
    """Wrapper around FastEmbed TextEmbedding for batch and query embeddings."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        logger.info("Initializing FastEmbed TextEmbedding with model: %s", model_name)
        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """
        Embed a batch of document texts into 384-dimensional dense vectors.
        """
        if not texts:
            return []
        embeddings = list(self._model.embed(texts))
        return [emb.tolist() if isinstance(emb, np.ndarray) else list(emb) for emb in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single search query into a 384-dimensional vector.
        """
        generator = self._model.query_embed(text)
        embedding = next(iter(generator))
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return list(embedding)


def get_embedding_service() -> FastEmbedService:
    """Lazy singleton provider for the FastEmbed service."""
    global _embedding_service
    if _embedding_service is None:
        settings = get_settings()
        _embedding_service = FastEmbedService(model_name=settings.embedding_model)
    return _embedding_service

