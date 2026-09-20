"""
Integration tests for WebSocket streaming endpoints (/ws/chat and /ws/documents/.../progress).
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.models.chat import ChatSession
from app.models.document import Document
from app.models.user import User
from tests.conftest import TestingSessionLocal

test_user = User(
    id=uuid.UUID("66666666-6666-6666-6666-666666666666"),
    clerk_id="user_ws_test_owner",
    email="ws_owner@untangle.ai",
    is_active=True,
)

test_doc_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
test_session_id = uuid.UUID("88888888-8888-8888-8888-888888888888")


@pytest.fixture(autouse=True)
def setup_ws_test_data():
    db = TestingSessionLocal()
    db.merge(test_user)

    doc = Document(
        id=test_doc_id,
        user_id=test_user.id,
        filename="ws_doc.pdf",
        file_path="uploads/ws_doc.pdf",
        file_size=1024,
        source_mode="research",
        status="ready",
        stats={"chunk_count": 3},
    )
    db.merge(doc)

    session = ChatSession(
        id=test_session_id,
        user_id=test_user.id,
        document_id=test_doc_id,
        title="WS Test Session",
        search_mode="local",
    )
    db.merge(session)
    db.commit()
    db.close()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_chat_unauthenticated(client):
    """Connecting to /ws/chat without token rejects connection."""
    with (
        pytest.raises(WebSocketDisconnect) as exc_info,
        client.websocket_connect(f"/ws/chat/{test_session_id}"),
    ):
        pass
    assert exc_info.value.code == 1008


def test_ws_chat_invalid_session(client):
    """Connecting to nonexistent session with valid auth rejects with 1008."""
    random_session_id = uuid.uuid4()
    with patch("app.api.v1.endpoints.ws.verify_clerk_token") as mock_verify:
        mock_verify.return_value = {"sub": test_user.clerk_id}
        with (
            pytest.raises(WebSocketDisconnect) as exc_info,
            client.websocket_connect(
                f"/ws/chat/{random_session_id}?token=valid_test_token"
            ),
        ):
            pass
        assert exc_info.value.code == 1008


def test_ws_chat_streaming_interaction(client):
    """Connected client sends message and receives streaming token + done events."""
    with patch("app.api.v1.endpoints.ws.verify_clerk_token") as mock_verify, patch(
        "app.services.chat_service.get_chat_model"
    ) as mock_model, patch(
        "app.services.chat_service.execute_local_search"
    ) as mock_local:
        mock_verify.return_value = {"sub": test_user.clerk_id}

        from app.services.retrieval.local_search import LocalSearchResult
        mock_local.return_value = LocalSearchResult(
            seed_entities=[],
            subgraph_nodes=[{"id": "GNN", "name": "GNN", "type": "CONCEPT", "description": "Graph network"}],
            subgraph_edges=[],
            text_chunks=[{"chunk_index": 1, "text": "Graph neural networks operate on graphs.", "score": 0.92}],
        )

        # Mock async streaming from LangChain chat model
        async def mock_astream(*args, **kwargs):
            chunk1 = MagicMock()
            chunk1.content = "GNNs "
            yield chunk1
            chunk2 = MagicMock()
            chunk2.content = "process graph-structured data [Chunk 1]."
            yield chunk2

        mock_llm = MagicMock()
        mock_llm.astream = mock_astream
        mock_model.return_value = mock_llm

        with client.websocket_connect(
            f"/ws/chat/{test_session_id}?token=valid_test_token"
        ) as ws:
            ws.send_json({"content": "Explain GNNs.", "search_mode": "local"})

            # Receive first token
            event1 = ws.receive_json()
            assert event1["type"] == "token"
            assert event1["content"] == "GNNs "

            # Receive second token
            event2 = ws.receive_json()
            assert event2["type"] == "token"
            assert "process graph-structured data" in event2["content"]

            # Receive done event with illuminated subgraph
            done_event = ws.receive_json()
            assert done_event["type"] == "done"
            assert "GNN" in done_event["subgraph"]["node_ids"]
            assert len(done_event["citations"]) >= 1


def test_ws_progress_unauthenticated(client):
    """Connecting to /ws/documents/.../progress without token rejects connection."""
    with (
        pytest.raises(WebSocketDisconnect) as exc_info,
        client.websocket_connect(f"/ws/documents/{test_doc_id}/progress"),
    ):
        pass
    assert exc_info.value.code == 1008


def test_ws_progress_ready_document(client):
    """Connecting to progress stream of already-ready document emits ready status and closes."""
    with patch("app.api.v1.endpoints.ws.verify_clerk_token") as mock_verify:
        mock_verify.return_value = {"sub": test_user.clerk_id}

        with client.websocket_connect(
            f"/ws/documents/{test_doc_id}/progress?token=valid_test_token"
        ) as ws:
            initial_msg = ws.receive_json()
            assert initial_msg["current_step"] == "ready"
            assert initial_msg["percent_complete"] == 100
