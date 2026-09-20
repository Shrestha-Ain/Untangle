"""
Integration tests for Chat Service and Chat REST API endpoints.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_active_user
from app.main import app
from app.models.document import Document
from app.models.user import User
from app.schemas.chat import ChatSessionCreate
from app.services import chat_service
from tests.conftest import TestingSessionLocal

test_user = User(
    id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
    clerk_id="user_test_chat_owner",
    email="chat_owner@untangle.ai",
    is_active=True,
)

test_doc_id = uuid.UUID("55555555-5555-5555-5555-555555555555")


def override_get_current_active_user():
    return test_user


@pytest.fixture(autouse=True)
def setup_test_data():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    db = TestingSessionLocal()
    db.merge(test_user)

    doc = Document(
        id=test_doc_id,
        user_id=test_user.id,
        filename="lecture_notes.pdf",
        file_path="uploads/lecture_notes.pdf",
        file_size=2048,
        source_mode="study",
        status="ready",
        stats={"chunk_count": 8, "entity_count": 14},
    )
    db.merge(doc)
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture
def client():
    return TestClient(app)


def test_route_query():
    """Verify local vs global heuristic query router."""
    assert chat_service.route_query("What is the definition of self-attention?") == "local"
    assert chat_service.route_query("Give me an overview of this entire document") == "global"
    assert chat_service.route_query("Summarize all chapters", requested_mode="auto") == "global"
    assert chat_service.route_query("Anything", requested_mode="global") == "global"
    assert chat_service.route_query("Summarize", requested_mode="local") == "local"


def test_create_and_list_chat_sessions_db():
    """Test Chat session DB CRUD operations."""
    db = TestingSessionLocal()
    session = chat_service.create_chat_session(
        db,
        user_id=test_user.id,
        data=ChatSessionCreate(
            document_id=test_doc_id,
            title="Transformer Discussion",
            search_mode="auto",
        ),
    )
    assert session.id is not None
    assert session.title == "Transformer Discussion"

    # List
    sessions = chat_service.list_chat_sessions(db, user_id=test_user.id)
    assert len(sessions) >= 1
    assert any(s.id == session.id for s in sessions)

    # Messages
    msg = chat_service.save_chat_message(
        db,
        session_id=session.id,
        role="user",
        content="What is attention?",
    )
    assert msg.id is not None

    messages = chat_service.get_session_messages(db, session_id=session.id)
    assert len(messages) == 1
    assert messages[0].content == "What is attention?"
    db.close()


def test_api_create_chat_session(client):
    """POST /api/v1/chat/sessions creates a new session."""
    payload = {
        "document_id": str(test_doc_id),
        "title": "Exam Prep Session",
        "search_mode": "local",
    }
    resp = client.post("/api/v1/chat/sessions", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Exam Prep Session"
    assert body["search_mode"] == "local"
    assert body["document_id"] == str(test_doc_id)


def test_api_create_session_invalid_doc(client):
    """POST /api/v1/chat/sessions with nonexistent doc returns 404."""
    random_doc_id = str(uuid.uuid4())
    payload = {
        "document_id": random_doc_id,
        "title": "Invalid Doc Session",
    }
    resp = client.post("/api/v1/chat/sessions", json=payload)
    assert resp.status_code == 404


def test_api_get_session_and_messages(client):
    """Test getting session metadata and messages via REST."""
    # Create session
    create_resp = client.post(
        "/api/v1/chat/sessions",
        json={"document_id": str(test_doc_id), "title": "History Test"},
    )
    session_id = create_resp.json()["id"]

    # Get single session
    get_resp = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == session_id

    # Get messages (initially empty)
    msg_resp = client.get(f"/api/v1/chat/sessions/{session_id}/messages")
    assert msg_resp.status_code == 200
    assert isinstance(msg_resp.json(), list)


def test_api_send_message_sync(client):
    """POST /api/v1/chat/sessions/{id}/messages executes synchronous conversation turn."""
    create_resp = client.post(
        "/api/v1/chat/sessions",
        json={"document_id": str(test_doc_id), "title": "Sync Turn Test"},
    )
    session_id = create_resp.json()["id"]

    with patch("app.services.chat_service.get_chat_model") as mock_model, patch(
        "app.services.chat_service.execute_local_search"
    ) as mock_local:
        from app.services.retrieval.local_search import LocalSearchResult
        mock_local.return_value = LocalSearchResult(
            seed_entities=[],
            subgraph_nodes=[{"id": "RNN", "name": "RNN", "type": "METHOD", "description": "Recurrent model"}],
            subgraph_edges=[],
            text_chunks=[{"chunk_index": 0, "text": "Recurrent neural networks process sequential data.", "score": 0.88}],
        )

        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "RNNs operate on sequential data step by step [Chunk 0]."
        mock_model.return_value = mock_llm

        send_resp = client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": "Explain how RNNs work.", "search_mode": "local"},
        )
        assert send_resp.status_code == 201
        body = send_resp.json()
        assert body["role"] == "assistant"
        assert "[Chunk 0]" in body["content"]
        assert len(body["citations"]) >= 1
