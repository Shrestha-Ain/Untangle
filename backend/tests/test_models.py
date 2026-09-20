"""
Unit tests for Database Models, Relationships, Schemas, and DB Initializers.

Tests:
1. User, Document, DocumentLink, IngestionJob, ChatSession, ChatMessage CRUD
2. Foreign key cascade deletion logic
3. Pydantic schema validation & serialization
4. Qdrant in-memory collection initialization
"""

import pytest
from qdrant_client import QdrantClient

from app.db.qdrant import (
    CHUNKS_COLLECTION,
    ENTITIES_COLLECTION,
    TOPICS_COLLECTION,
    init_qdrant_collections,
)
from app.models.chat import ChatMessage, ChatSession
from app.models.document import Document, DocumentLink, IngestionJob
from app.models.user import User
from app.schemas.chat import (
    ChatSessionRead,
    ChatStreamDoneEvent,
    SubgraphData,
)
from app.schemas.document import DocumentRead
from tests.conftest import TestingSessionLocal


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_document_and_user_relationship(db):
    """Verify document creation and back-population to user."""
    user = User(clerk_id="user_clerk_123", email="scholar@research.edu")
    db.add(user)
    db.commit()
    db.refresh(user)

    doc = Document(
        user_id=user.id,
        filename="attention_is_all_you_need.pdf",
        file_path="/uploads/attention.pdf",
        file_size=1024000,
        source_mode="research",
        display_title="Attention Is All You Need",
        status="ready",
        stats={
            "chunk_count": 32,
            "entity_count": 45,
            "community_count": 4,
            "chapter_count": 0,
        },
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    assert doc.id is not None
    assert doc.user_id == user.id
    assert doc.user.email == "scholar@research.edu"
    assert len(user.documents) == 1
    assert user.documents[0].filename == "attention_is_all_you_need.pdf"

    # Test Pydantic serialization
    schema = DocumentRead.model_validate(doc)
    assert schema.display_title == "Attention Is All You Need"
    assert schema.stats["chunk_count"] == 32


def test_document_link_and_ingestion_job(db):
    """Verify cross-source links and ingestion telemetry tracking."""
    user = User(clerk_id="user_study_456")
    db.add(user)
    db.commit()

    doc1 = Document(
        user_id=user.id,
        filename="textbook_ch1.pdf",
        file_path="/uploads/ch1.pdf",
        source_mode="study",
        display_title="Deep Learning Foundations",
    )
    doc2 = Document(
        user_id=user.id,
        filename="transformer_paper.pdf",
        file_path="/uploads/trans.pdf",
        source_mode="research",
        display_title="Transformer Architecture",
    )
    db.add_all([doc1, doc2])
    db.commit()

    link = DocumentLink(
        source_document_id=doc1.id,
        target_document_id=doc2.id,
        topic_id="Self-Attention",
        link_reason="Prerequisite deep-dive on attention mechanisms",
        link_mode="auto",
        status="suggested",
    )
    job = IngestionJob(
        document_id=doc1.id,
        task_id="celery_task_abc",
        status="running",
        current_step="extract",
        percent_complete=55,
        towers_built=12,
        roads_laid=18,
    )
    db.add_all([link, job])
    db.commit()

    assert len(doc1.links_as_source) == 1
    assert doc1.links_as_source[0].target_document.display_title == "Transformer Architecture"
    assert len(doc1.ingestion_jobs) == 1
    assert doc1.ingestion_jobs[0].percent_complete == 55


def test_chat_session_and_message_cascade(db):
    """Verify chat session, message creation with grounded subgraph, and cascade deletion."""
    user = User(clerk_id="user_chat_789")
    db.add(user)
    db.commit()

    doc = Document(
        user_id=user.id,
        filename="graphrag_spec.pdf",
        file_path="/uploads/spec.pdf",
    )
    db.add(doc)
    db.commit()

    session = ChatSession(
        user_id=user.id,
        document_id=doc.id,
        title="Exploring Graph Communities",
        search_mode="local",
    )
    db.add(session)
    db.commit()

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content="What is Scaled Dot-Product Attention?",
    )
    asst_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content="Scaled Dot-Product Attention computes attention weights...",
        retrieved_subgraph={"node_ids": ["entity_attention", "entity_softmax"], "edge_ids": ["rel_att_soft"]},
        citations=[{"chunk_id": "chunk_4", "text": "Softmax(QK^T / sqrt(d_k))V"}],
        latency_ms=145,
    )
    db.add_all([user_msg, asst_msg])
    db.commit()

    assert len(session.messages) == 2
    assert session.messages[1].role == "assistant"
    assert session.messages[1].retrieved_subgraph["node_ids"] == ["entity_attention", "entity_softmax"]

    # Verify Pydantic validation
    session_read = ChatSessionRead.model_validate(session)
    assert len(session_read.messages) == 2
    assert session_read.messages[1].latency_ms == 145

    # Test stream done event validation
    done_event = ChatStreamDoneEvent(
        citations=[{"chunk_id": "c1", "text": "Formula 1"}],
        subgraph=SubgraphData(node_ids=["n1"], edge_ids=["e1"]),
        search_mode="local",
        latency_ms=150,
    )
    assert done_event.subgraph.node_ids == ["n1"]

    # Cascade deletion check: deleting document should delete chat session and messages
    db.delete(doc)
    db.commit()
    assert db.query(ChatSession).filter(ChatSession.id == session.id).first() is None
    assert db.query(ChatMessage).filter(ChatMessage.session_id == session.id).first() is None


def test_qdrant_in_memory_initialization():
    """Verify Qdrant collection initialization on in-memory instance."""
    client = QdrantClient(":memory:")
    init_qdrant_collections(client=client, dim=384)

    collections = [c.name for c in client.get_collections().collections]
    assert CHUNKS_COLLECTION in collections
    assert ENTITIES_COLLECTION in collections
    assert TOPICS_COLLECTION in collections

    client.close()

