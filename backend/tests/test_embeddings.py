"""
Unit tests for FastEmbed local embedding service.
"""

import math

from app.llm.embeddings import FastEmbedService, get_embedding_service


def test_fastembed_service_dimension_and_norm():
    """Verify that FastEmbed produces 384-dimensional normalized vectors on CPU."""
    service = get_embedding_service()
    assert isinstance(service, FastEmbedService)

    # 1. Test batch document embedding
    texts = [
        "Scaled Dot-Product Attention calculates attention weights via softmax.",
        "Graph Neural Networks aggregate neighbor messages across edges.",
    ]
    embeddings = service.embed_documents(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384

    # 2. Test query embedding
    query_emb = service.embed_query("What is self-attention?")
    assert len(query_emb) == 384

    # 3. Verify vectors are normalized (L2 norm ≈ 1.0)
    norm = math.sqrt(sum(x * x for x in query_emb))
    assert abs(norm - 1.0) < 1e-2


def test_fastembed_empty_input():
    """Verify empty input returns empty list."""
    service = get_embedding_service()
    assert service.embed_documents([]) == []

